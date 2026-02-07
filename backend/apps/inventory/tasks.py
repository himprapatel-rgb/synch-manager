"""Celery tasks for SNMP polling and device management."""
import logging
from celery import shared_task
from django.utils import timezone
from .models import NetworkElement
from .device_drivers import get_driver

logger = logging.getLogger(__name__)


@shared_task
def poll_network_elements():
    """
    Poll all managed network elements via SNMP.
    Runs every 5 minutes to collect device status, metrics, and update database.
    """
    logger.info("Starting SNMP polling for all managed network elements")
    
    # Get all managed devices
    managed_elements = NetworkElement.objects.filter(
        management_state='MANAGED'
    )
    
    poll_results = {
        'success': 0,
        'failed': 0,
        'total': managed_elements.count()
    }
    
    for element in managed_elements:
        try:
            logger.info(f"Polling {element.name} ({element.ip_address})")
            
            # Get the appropriate driver for this device type
            driver = get_driver(element.ne_type)
            
            if driver:
                # Poll SNMP data
                snmp_data = driver.poll_device(
                    ip_address=element.ip_address,
                    community=element.snmp_community,
                    version=element.snmp_version
                )
                
                # Update device with polled data
                if snmp_data:
                    element.sys_descr = snmp_data.get('sysDescr', '')
                    element.sys_object_id = snmp_data.get('sysObjectID', '')
                    element.firmware_version = snmp_data.get('firmware_version', '')
                    element.serial_number = snmp_data.get('serial_number', '')
                    element.hardware_revision = snmp_data.get('hardware_revision', '')
                    element.uptime_seconds = snmp_data.get('uptime', 0)
                    element.last_polled = timezone.now()
                    element.save()
                    
                    poll_results['success'] += 1
                    logger.info(f"Successfully polled {element.name}")
                else:
                    poll_results['failed'] += 1
                    logger.warning(f"No data returned from {element.name}")
            else:
                poll_results['failed'] += 1
                logger.warning(f"No driver found for {element.ne_type}")
                
        except Exception as e:
            poll_results['failed'] += 1
            logger.error(f"Error polling {element.name}: {str(e)}")
            # Set management state to unavailable on repeated failures
            element.management_state = 'UNAVAILABLE'
            element.save()
    
    logger.info(f"SNMP polling completed. Success: {poll_results['success']}, "
                f"Failed: {poll_results['failed']}, Total: {poll_results['total']}")
    
    return poll_results


@shared_task
def discover_network_element(element_id):
    """
    Perform initial SNMP discovery on a single network element.
    """
    try:
        element = NetworkElement.objects.get(id=element_id)
        logger.info(f"Discovering {element.name} ({element.ip_address})")
        
        driver = get_driver(element.ne_type)
        
        if driver:
            snmp_data = driver.discover_device(
                ip_address=element.ip_address,
                community=element.snmp_community,
                version=element.snmp_version
            )
            
            if snmp_data:
                element.sys_descr = snmp_data.get('sysDescr', '')
                element.sys_object_id = snmp_data.get('sysObjectID', '')
                element.firmware_version = snmp_data.get('firmware_version', '')
                element.serial_number = snmp_data.get('serial_number', '')
                element.hardware_revision = snmp_data.get('hardware_revision', '')
                element.uptime_seconds = snmp_data.get('uptime', 0)
                element.last_discovered = timezone.now()
                element.last_polled = timezone.now()
                element.management_state = 'MANAGED'
                element.save()
                
                logger.info(f"Successfully discovered {element.name}")
                return True
        
        logger.error(f"Failed to discover {element.name}")
        return False
        
    except NetworkElement.DoesNotExist:
        logger.error(f"Network element {element_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error discovering element {element_id}: {str(e)}")
        return False
