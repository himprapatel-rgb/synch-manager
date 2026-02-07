"""
Digital Twin simulation engine for Synch-Manager.

Responsibilities:
- Advance time for running scenarios
- Apply scenario events to VirtualNE objects
- Update GNSS / clock / link state
- Maintain basic holdover drift and time error

This is intentionally minimal but functional. It can be called
from a management command or a periodic task scheduler (Celery,
Django-Q, cron, etc.).
"""

import logging
from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from .models import Scenario, VirtualNE

logger = logging.getLogger(__name__)


# --- Oscillator parameters for holdover (simplified) ---

OSC_PARAMS = {
    # Allan deviation at 1s, aging per day (fractional)
    "OCXO": {"adev_1s": 1e-11, "aging_per_day": 1e-10},
    "RUBIDIUM": {"adev_1s": 3e-11, "aging_per_day": 5e-12},
    "CSAC": {"adev_1s": 1.5e-10, "aging_per_day": 3e-11},
    "CESIUM": {"adev_1s": 1e-11, "aging_per_day": 0.0},
}


def _compute_holdover_time_error_ns(oscillator_type: str, elapsed_seconds: int) -> float:
    """
    Compute approximate time error during holdover for a given oscillator.

    TimeError(T) ≈ freq_offset * T + (aging_rate * T^2) / 2

    - freq_offset ≈ ADEV at 1s
    - aging_rate = aging_per_day / 86400

    Returns time error in ns.
    """
    params = OSC_PARAMS.get(oscillator_type.upper())
    if not params:
        return 0.0

    T = float(elapsed_seconds)
    freq_offset = params["adev_1s"]
    aging_rate = params["aging_per_day"] / 86400.0

    time_error_sec = freq_offset * T + aging_rate * (T ** 2) / 2.0
    return time_error_sec * 1e9  # ns


# --- Scenario application helpers ---


def _apply_instant_change(ne: VirtualNE, parameter: str, to_value):
    """
    Apply an 'instant' change from a scenario event to a VirtualNE.
    Parameter is a dotted path like 'gnss.lock_state' or 'clock.mode'.
    """
    try:
        # Map dotted parameter names to model fields
        mapping = {
            "gnss.lock_state": "gnss_lock_state",
            "gnss.num_satellites": "gnss_num_satellites",
            "gnss.avg_cn0": "gnss_avg_cn0",
            "gnss.hdop": "gnss_hdop",
            "gnss.position_valid": "gnss_position_valid",
            "gnss.antenna_status": "gnss_antenna_status",
            "gnss.jam_indicator": "gnss_jam_indicator",
            "gnss.spoof_indicator": "gnss_spoof_indicator",
            "gnss.osnma_status": "gnss_osnma_status",
            "clock.mode": "clock_mode",
            "clock.oscillator_type": "oscillator_type",
            "clock.beam_status": "beam_status",
            "clock.tube_hours": "tube_hours",
            "clock.tube_life_percent": "tube_life_percent",
            "ptp.clock_class": "ptp_clock_class",
            "ptp.clock_accuracy": "ptp_clock_accuracy",
            "ptp.port_state": "ptp_port_state",
            "ptp.gm_clock_id": "ptp_gm_clock_id",
            "ptp.time_offset_ns": "ptp_time_offset_ns",
            "ptp.path_delay_ns": "ptp_path_delay_ns",
            "ptp.num_clients": "ptp_num_clients",
            "link.state": None,  # handled via VirtualLink, not here
        }

        field_name = mapping.get(parameter)
        if not field_name:
            logger.debug("Unknown parameter '%s' for VirtualNE %s", parameter, ne.id)
            return

        setattr(ne, field_name, to_value)
    except Exception as exc:
        logger.error("Failed to apply instant change %s=%s to VirtualNE %s: %s",
                     parameter, to_value, ne.id, exc)


def _update_holdover(ne: VirtualNE, now):
    """
    Update holdover elapsed time and estimated time error if NE is in HOLDOVER.
    """
    if ne.clock_mode != "HOLDOVER":
        return

    if ne.holdover_start_time is None:
        # Start holdover now
        ne.holdover_start_time = now
        ne.holdover_elapsed_seconds = 0
        ne.estimated_time_error_ns = 0.0
        return

    elapsed = (now - ne.holdover_start_time).total_seconds()
    ne.holdover_elapsed_seconds = int(elapsed)
    ne.estimated_time_error_ns = _compute_holdover_time_error_ns(
        ne.oscillator_type, ne.holdover_elapsed_seconds
    )


def _tick_virtual_ne(ne: VirtualNE, now):
    """
    Advance one tick for a VirtualNE:
    - Increase uptime
    - Update holdover drift
    Future: add small noise to GNSS, PTP, etc.
    """
    ne.uptime_seconds += 1

    # Update holdover
    _update_holdover(ne, now)

    # Placeholder for additional dynamics (noise, etc.)
    # e.g. simulate small random fluctuations in gnss_avg_cn0, ptp_time_offset_ns


# --- Scenario engine main tick ---


def run_scenario_tick(max_scenarios: int = 5):
    """
    Run one tick of all active scenarios.

    This function is intended to be called periodically (e.g. every second)
    by a scheduler (Celery beat, cron, systemd timer, etc.).

    - Finds running scenarios.
    - Computes elapsed time.
    - Applies any events due at this time.
    - Advances VirtualNE states (uptime, holdover).

    Args:
        max_scenarios: limit number of scenarios processed per tick.
    """
    now = timezone.now()
    running_scenarios = (
        Scenario.objects
        .select_for_update(skip_locked=True)
        .filter(is_running=True)
        .order_by("id")[:max_scenarios]
    )

    if not running_scenarios:
        return

    for scenario in running_scenarios:
        with transaction.atomic():
            _process_scenario_tick(scenario, now)


def _process_scenario_tick(scenario: Scenario, now):
    """
    Process a single scenario tick inside a DB transaction.
    """
    if scenario.started_at is None:
        # First time: start now
        scenario.started_at = now
        scenario.last_tick_at = now
        scenario.save(update_fields=["started_at", "last_tick_at"])
        return

    # Compute elapsed scenario time
    elapsed = (now - scenario.started_at).total_seconds()
    definition = scenario.definition or {}

    duration_minutes = float(definition.get("duration_minutes", 0))
    duration_seconds = int(duration_minutes * 60)

    # Stop scenario if duration exceeded
    if duration_seconds > 0 and elapsed > duration_seconds:
        scenario.is_running = False
        scenario.last_tick_at = now
        scenario.save(update_fields=["is_running", "last_tick_at"])
        logger.info("Scenario '%s' completed (elapsed=%.1fs)", scenario.name, elapsed)
        return

    events = definition.get("events", [])
    # Apply events whose time_offset_seconds <= elapsed and > last_tick_elapsed
    last_tick_elapsed = 0.0
    if scenario.last_tick_at:
        last_tick_elapsed = (scenario.last_tick_at - scenario.started_at).total_seconds()

    # Cache NEs by name for this topology to avoid repeated queries
    ne_cache = {}
    if scenario.default_topology_id:
        for ne in VirtualNE.objects.filter(topology_id=scenario.default_topology_id):
            ne_cache[ne.ne_name] = ne

    for event in events:
        t_offset = float(event.get("time_offset_seconds", 0))
        if not (last_tick_elapsed < t_offset <= elapsed):
            continue

        targets = event.get("targets", [])
        for target in targets:
            ne_name = target.get("virtual_ne")
            parameter = target.get("parameter")
            transition = target.get("transition", "instant")
            to_value = target.get("to_value")

            if not ne_name or not parameter:
                continue

            ne = ne_cache.get(ne_name)
            if not ne:
                logger.debug("Scenario '%s': VirtualNE '%s' not found", scenario.name, ne_name)
                continue

            if transition == "instant":
                _apply_instant_change(ne, parameter, to_value)
            else:
                # For now, only instant is implemented; other transitions
                # (linear_decrease, etc.) can be added later.
                pass

    # Advance all NEs in the scenario's topology by one tick
    if scenario.default_topology_id:
        nes = VirtualNE.objects.filter(topology_id=scenario.default_topology_id)
        for ne in nes:
            _tick_virtual_ne(ne, now)
            ne.save()

    scenario.last_tick_at = now
    scenario.save(update_fields=["last_tick_at"])
