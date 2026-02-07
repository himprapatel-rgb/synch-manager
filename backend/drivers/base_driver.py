"""Abstract base class for all NE drivers in Synch-Manager.

Every network element driver must implement these methods so the
platform can poll inventory, faults, and performance data uniformly.
"""
from abc import ABC, abstractmethod
from typing import Any
from pysnmp.hlapi import (
    getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity,
)


class BaseDriver(ABC):
    """Base driver interface for synchronization network elements."""

    NE_TYPE: str = 'generic'
    SUPPORTED_LINK_TYPES: list = ['ptp']  # override in subclasses

    # -- SNMP helpers ------------------------------------------------

    def snmp_get(self, host: str, oid: str, community: str = 'public',
                 port: int = 161) -> Any:
        """Perform a single SNMP GET and return the value."""
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, port), timeout=5, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
        error_indication, error_status, _, var_binds = next(iterator)
        if error_indication or error_status:
            return None
        return var_binds[0][1] if var_binds else None

    # -- Abstract interface every driver must implement ---------------

    @abstractmethod
    def get_inventory(self, host: str, community: str) -> dict:
        """Return inventory data (firmware, hardware, serial, etc.)."""

    @abstractmethod
    def get_alarms(self, host: str, community: str) -> list[dict]:
        """Return current active alarms / fault status."""

    @abstractmethod
    def get_performance(self, host: str, community: str) -> dict:
        """Return performance metrics (clock offset, RTT, etc.)."""

    @abstractmethod
    def get_clock_quality(self, host: str, community: str) -> dict:
        """Return clock quality level (ePRTC, PRC, PRS, etc.)."""

    @abstractmethod
    def get_gnss_status(self, host: str, community: str) -> dict:
        """Return GNSS receiver status (lock, satellites, health)."""

    def get_link_type(self) -> str:
        """Return the highest-quality link type this NE supports."""
        if 'white_rabbit' in self.SUPPORTED_LINK_TYPES:
            return 'white_rabbit'
        if 'ptp_synce' in self.SUPPORTED_LINK_TYPES:
            return 'ptp_synce'
        return 'ptp'
