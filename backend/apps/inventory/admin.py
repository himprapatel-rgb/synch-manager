from django.contrib import admin
from .models import NetworkElementGroup, NetworkElement, Card, Port, TimingLink


@admin.register(NetworkElementGroup)
class NetworkElementGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']


@admin.register(NetworkElement)
class NetworkElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'ne_type', 'ip_address', 'management_state', 'worst_alarm', 'trust_score']
    list_filter = ['ne_type', 'management_state', 'worst_alarm']
    search_fields = ['name', 'ip_address']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['network_element', 'slot', 'card_type', 'operational_state']
    list_filter = ['operational_state']


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ['card', 'port_number', 'port_type', 'direction', 'operational_state']
    list_filter = ['port_type', 'direction', 'operational_state']


@admin.register(TimingLink)
class TimingLinkAdmin(admin.ModelAdmin):
    list_display = ['source_port', 'destination_port', 'link_type', 'is_active']
    list_filter = ['link_type', 'is_active']
