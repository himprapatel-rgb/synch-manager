"""NE driver plugin registry for Synch-Manager.

Each driver maps SNMP OIDs to a common data model for a specific
network element type (TimeProvider, White Rabbit Switch, etc.).
"""
from .base_driver import BaseDriver
from .white_rabbit_switch import WhiteRabbitSwitchDriver
from .timeprovider5000 import TimeProvider5000Driver

# Registry: NE type string -> driver class
DRIVER_REGISTRY = {
    'white_rabbit_switch': WhiteRabbitSwitchDriver,
    'timeprovider_5000': TimeProvider5000Driver,
}


def get_driver(ne_type: str) -> BaseDriver:
    """Return the driver class for a given NE type string."""
    driver_cls = DRIVER_REGISTRY.get(ne_type)
    if driver_cls is None:
        raise ValueError(f'No driver registered for NE type: {ne_type}')
    return driver_cls()


__all__ = ['BaseDriver', 'WhiteRabbitSwitchDriver', 'TimeProvider5000Driver',
           'DRIVER_REGISTRY', 'get_driver']
