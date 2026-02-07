"""
Configuration Management Serializers for Synch-Manager.

Policy-based configuration management with compliance auditing,
GitOps-style version control, and Zero Trust timing validation.
"""

from rest_framework import serializers

from .models import (
    ConfigurationPolicy, PolicyGroup, PolicyAssignment,
    ComplianceAudit, ConfigurationSnapshot, FirmwarePolicy,
    TimingSourcePriority,
)


class ConfigurationPolicySerializer(serializers.ModelSerializer):
    """Serializer for reusable configuration policy templates."""
    policy_type_display = serializers.CharField(
        source='get_policy_type_display', read_only=True,
    )

    class Meta:
        model = ConfigurationPolicy
        fields = [
            'id', 'name', 'description', 'policy_type',
            'policy_type_display', 'config_data', 'version',
            'is_active', 'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PolicyGroupSerializer(serializers.ModelSerializer):
    """Serializer for policy groups applied to NEs."""
    policies = ConfigurationPolicySerializer(many=True, read_only=True)
    policy_ids = serializers.PrimaryKeyRelatedField(
        queryset=ConfigurationPolicy.objects.all(),
        many=True, write_only=True, source='policies',
    )

    class Meta:
        model = PolicyGroup
        fields = [
            'id', 'name', 'description', 'policies',
            'policy_ids', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PolicyAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for policy assignment tracking."""
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )

    class Meta:
        model = PolicyAssignment
        fields = [
            'id', 'policy_group', 'network_element', 'status',
            'status_display', 'applied_at', 'applied_by',
            'rollback_data', 'error_message', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ComplianceAuditSerializer(serializers.ModelSerializer):
    """Serializer for compliance audit results."""
    result_display = serializers.CharField(
        source='get_result_display', read_only=True,
    )

    class Meta:
        model = ComplianceAudit
        fields = [
            'id', 'network_element', 'policy', 'result',
            'result_display', 'expected_config', 'actual_config',
            'deviations', 'audited_at', 'audited_by',
        ]
        read_only_fields = ['id', 'audited_at']


class ConfigurationSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for point-in-time NE configuration snapshots."""

    class Meta:
        model = ConfigurationSnapshot
        fields = [
            'id', 'network_element', 'config_data',
            'snapshot_type', 'taken_at', 'taken_by', 'notes',
        ]
        read_only_fields = ['id', 'taken_at']


class FirmwarePolicySerializer(serializers.ModelSerializer):
    """Serializer for approved firmware version policies."""

    class Meta:
        model = FirmwarePolicy
        fields = [
            'id', 'ne_type', 'approved_version',
            'minimum_version', 'release_notes_url',
            'is_mandatory', 'deadline',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimingSourcePrioritySerializer(serializers.ModelSerializer):
    """Serializer for Zero Trust timing source priorities."""
    source_type_display = serializers.CharField(
        source='get_source_type_display', read_only=True,
    )

    class Meta:
        model = TimingSourcePriority
        fields = [
            'id', 'network_element', 'source_type',
            'source_type_display', 'priority',
            'trust_threshold', 'enabled',
        ]
        read_only_fields = ['id']
