"""
Digital Twin models for Synch-Manager.

These models are designed to:
- Reuse the same concepts as real NEs (FCAPS in TimePictra) [file:2][file:3]
- Cleanly represent virtual topologies, virtual NEs, links, and scenarios
- Be simple enough to implement now, but flexible enough to extend later
"""

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField, JSONField


class VirtualTopology(models.Model):
    """
    A virtual timing network (sites + links) used by the Sync Digital Twin.
    """
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: tag / owner for multi-tenant or lab environments
    owner = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"VirtualTopology(id={self.id}, name={self.name})"


class VirtualNE(models.Model):
    """
    A virtual Network Element that mimics a real timing device:
    TP4100, LANTIME, OSA, PRS-4400, etc. [file:2][file:3]
    """
    topology = models.ForeignKey(
        VirtualTopology,
        related_name="virtual_nes",
        on_delete=models.CASCADE,
    )

    # Identity
    ne_name = models.CharField(max_length=128)
    ne_type = models.CharField(max_length=128)   # e.g. "TimeProvider 4100"
    vendor = models.CharField(max_length=64)     # e.g. "Microchip", "Meinberg"
    is_virtual = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=256, blank=True)
    serial_number = models.CharField(max_length=128, blank=True)
    firmware_version = models.CharField(max_length=128, blank=True)

    # Management status
    managed = models.BooleanField(default=True)
    reachable = models.BooleanField(default=True)
    uptime_seconds = models.BigIntegerField(default=0)

    # GNSS status (compact version; details in gnss_state JSON if needed)
    gnss_lock_state = models.CharField(
        max_length=16,
        choices=[
            ("LOCKED", "LOCKED"),
            ("ACQUIRING", "ACQUIRING"),
            ("UNLOCKED", "UNLOCKED"),
        ],
        default="LOCKED",
    )
    gnss_num_satellites = models.IntegerField(default=0)
    gnss_avg_cn0 = models.FloatField(default=0.0)  # dB-Hz
    gnss_constellations = ArrayField(
        base_field=models.CharField(max_length=16),
        default=list,
        blank=True,
    )
    gnss_hdop = models.FloatField(default=0.0)
    gnss_position_valid = models.BooleanField(default=True)
    gnss_antenna_status = models.CharField(
        max_length=16,
        choices=[
            ("OK", "OK"),
            ("SHORT", "SHORT"),
            ("OPEN", "OPEN"),
        ],
        default="OK",
    )
    gnss_jam_indicator = models.FloatField(default=0.0)   # 0.0 - 1.0
    gnss_spoof_indicator = models.FloatField(default=0.0) # 0.0 - 1.0
    gnss_osnma_status = models.CharField(
        max_length=24,
        choices=[
            ("AUTHENTICATED", "AUTHENTICATED"),
            ("NOT_AVAILABLE", "NOT_AVAILABLE"),
            ("FAILED", "FAILED"),
        ],
        default="NOT_AVAILABLE",
    )

    # PTP status
    ptp_clock_class = models.IntegerField(default=248)  # 6,7,248, etc.
    ptp_clock_accuracy = models.CharField(max_length=8, default="0xFE")
    ptp_port_state = models.CharField(
        max_length=16,
        choices=[
            ("MASTER", "MASTER"),
            ("SLAVE", "SLAVE"),
            ("PASSIVE", "PASSIVE"),
            ("LISTENING", "LISTENING"),
        ],
        default="MASTER",
    )
    ptp_gm_clock_id = models.CharField(max_length=32, blank=True)
    ptp_time_offset_ns = models.FloatField(default=0.0)
    ptp_path_delay_ns = models.FloatField(default=0.0)
    ptp_num_clients = models.IntegerField(default=0)
    synce_status = models.CharField(
        max_length=16,
        choices=[
            ("LOCKED", "LOCKED"),
            ("HOLDOVER", "HOLDOVER"),
            ("FREE_RUN", "FREE_RUN"),
        ],
        default="LOCKED",
    )

    # Oscillator / clock
    oscillator_type = models.CharField(
        max_length=16,
        choices=[
            ("OCXO", "OCXO"),
            ("RUBIDIUM", "RUBIDIUM"),
            ("CESIUM", "CESIUM"),
            ("CSAC", "CSAC"),
        ],
        default="OCXO",
    )
    clock_mode = models.CharField(
        max_length=16,
        choices=[
            ("NORMAL", "NORMAL"),
            ("HOLDOVER", "HOLDOVER"),
            ("FREE_RUN", "FREE_RUN"),
            ("WARMUP", "WARMUP"),
        ],
        default="NORMAL",
    )
    holdover_start_time = models.DateTimeField(null=True, blank=True)
    holdover_elapsed_seconds = models.BigIntegerField(default=0)
    estimated_time_error_ns = models.FloatField(default=0.0)
    frequency_offset_ppb = models.FloatField(default=0.0)

    # Cesium-specific
    beam_status = models.CharField(
        max_length=16,
        choices=[
            ("NORMAL", "NORMAL"),
            ("DEGRADED", "DEGRADED"),
            ("FAILED", "FAILED"),
        ],
        default="NORMAL",
    )
    tube_hours = models.BigIntegerField(default=0)
    tube_life_percent = models.FloatField(default=100.0)

    # Performance snapshot (can be expanded with time-series in another table)
    current_mtie_ns = models.FloatField(default=0.0)
    current_tdev_ns = models.FloatField(default=0.0)
    phase_error_ns = models.FloatField(default=0.0)

    # Extra JSON for future extension (e.g. vendor-specific data)
    extra_state = JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("topology", "ne_name")

    def __str__(self):
        return f"VirtualNE(id={self.id}, name={self.ne_name}, vendor={self.vendor})"


class VirtualLink(models.Model):
    """
    A virtual sync link (PTP, SyncE, NTP, White Rabbit) between two VirtualNEs.
    """
    topology = models.ForeignKey(
        VirtualTopology,
        related_name="virtual_links",
        on_delete=models.CASCADE,
    )
    src = models.ForeignKey(
        VirtualNE,
        related_name="outgoing_links",
        on_delete=models.CASCADE,
    )
    dst = models.ForeignKey(
        VirtualNE,
        related_name="incoming_links",
        on_delete=models.CASCADE,
    )

    link_type = models.CharField(
        max_length=16,
        choices=[
            ("PTP", "PTP"),
            ("SYNCE", "SYNCE"),
            ("NTP", "NTP"),
            ("WHITE_RABBIT", "WHITE_RABBIT"),
        ],
        default="PTP",
    )
    link_state = models.CharField(
        max_length=8,
        choices=[
            ("UP", "UP"),
            ("DOWN", "DOWN"),
        ],
        default="UP",
    )
    link_delay_ns = models.FloatField(default=0.0)

    # Optional human-readable label
    label = models.CharField(max_length=128, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["topology", "link_type"]),
        ]

    def __str__(self):
        return f"VirtualLink(id={self.id}, src={self.src.ne_name}, dst={self.dst.ne_name}, type={self.link_type})"


class Scenario(models.Model):
    """
    A GNSS/Sync scenario definition as JSON (events, timings, targets).

    The Digital Twin engine will parse this JSON and apply time-based updates
    to VirtualNE objects. [web:413][web:414][web:409]
    """
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    # Raw JSON definition (events, transitions, parameters)
    definition = JSONField()

    # Optional: scenario is associated with a topology by default
    default_topology = models.ForeignKey(
        VirtualTopology,
        related_name="scenarios",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Simple flags to show if scenario is currently in use
    is_running = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    last_tick_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Scenario(id={self.id}, name={self.name})"
