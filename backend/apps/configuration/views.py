"""
Configuration Management Views for Synch-Manager.

Policy CRUD, compliance auditing, config snapshots, firmware policies,
and Zero Trust timing source priority management.
"""

from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    ConfigurationPolicy, PolicyGroup, PolicyAssignment,
    ComplianceAudit, ConfigurationSnapshot, FirmwarePolicy,
    TimingSourcePriority,
)


# --- Serializers (inline for this app) ---


class ConfigurationPolicySerializer(drf_serializers.ModelSerializer):
    policy_type_display = drf_serializers.CharField(
        source='get_policy_type_display', read_only=True,
    )

    class Meta:
        model = ConfigurationPolicy
        fields = '__all__'


class PolicyGroupSerializer(drf_serializers.ModelSerializer):
    policies = ConfigurationPolicySerializer(many=True, read_only=True)
    policy_ids = drf_serializers.PrimaryKeyRelatedField(
        queryset=ConfigurationPolicy.objects.all(),
        many=True, write_only=True, source='policies',
    )

    class Meta:
        model = PolicyGroup
        fields = '__all__'


class PolicyAssignmentSerializer(drf_serializers.ModelSerializer):
    status_display = drf_serializers.CharField(
        source='get_status_display', read_only=True,
    )

    class Meta:
        model = PolicyAssignment
        fields = '__all__'


class ComplianceAuditSerializer(drf_serializers.ModelSerializer):
    result_display = drf_serializers.CharField(
        source='get_result_display', read_only=True,
    )

    class Meta:
        model = ComplianceAudit
        fields = '__all__'


class ConfigurationSnapshotSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ConfigurationSnapshot
        fields = '__all__'


class FirmwarePolicySerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = FirmwarePolicy
        fields = '__all__'


class TimingSourcePrioritySerializer(drf_serializers.ModelSerializer):
    source_type_display = drf_serializers.CharField(
        source='get_source_type_display', read_only=True,
    )

    class Meta:
        model = TimingSourcePriority
        fields = '__all__'


# --- ViewSets ---


class ConfigurationPolicyViewSet(viewsets.ModelViewSet):
    """CRUD for configuration policies."""

    queryset = ConfigurationPolicy.objects.all()
    serializer_class = ConfigurationPolicySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['policy_type', 'is_active']

    @action(detail=True, methods=['post'], url_path='bump-version')
    def bump_version(self, request, pk=None):
        """Increment policy version."""
        policy = self.get_object()
        policy.version += 1
        policy.save(update_fields=['version', 'updated_at'])
        return Response(ConfigurationPolicySerializer(policy).data)


class PolicyGroupViewSet(viewsets.ModelViewSet):
    """CRUD for policy groups."""

    queryset = PolicyGroup.objects.prefetch_related('policies').all()
    serializer_class = PolicyGroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], url_path='apply')
    def apply_to_ne(self, request, pk=None):
        """Apply policy group to a network element."""
        group = self.get_object()
        ne_id = request.data.get('ne_id')
        if not ne_id:
            return Response(
                {'error': 'ne_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment, created = PolicyAssignment.objects.get_or_create(
            policy_group=group,
            network_element_id=ne_id,
            defaults={
                'status': PolicyAssignment.Status.PENDING,
                'applied_by': request.user.username,
            },
        )
        if not created:
            assignment.status = PolicyAssignment.Status.PENDING
            assignment.applied_by = request.user.username
            assignment.save()
        return Response(
            PolicyAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED if created
            else status.HTTP_200_OK,
        )


class PolicyAssignmentViewSet(viewsets.ModelViewSet):
    """Track and manage policy assignments to NEs."""

    queryset = PolicyAssignment.objects.select_related(
        'policy_group', 'network_element'
    ).all()
    serializer_class = PolicyAssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'network_element']

    @action(detail=True, methods=['post'], url_path='rollback')
    def rollback(self, request, pk=None):
        """Roll back a policy assignment to previous config."""
        assignment = self.get_object()
        if not assignment.rollback_data:
            return Response(
                {'error': 'No rollback data available'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment.status = PolicyAssignment.Status.ROLLED_BACK
        assignment.save(update_fields=['status'])
        return Response(PolicyAssignmentSerializer(assignment).data)


class ComplianceAuditViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of compliance audit results."""

    queryset = ComplianceAudit.objects.select_related(
        'network_element', 'policy'
    ).all()
    serializer_class = ComplianceAuditSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['result', 'network_element', 'policy']

    @action(detail=False, methods=['post'], url_path='trigger')
    def trigger_audit(self, request):
        """Trigger a compliance audit for a specific NE."""
        ne_id = request.data.get('ne_id')
        policy_id = request.data.get('policy_id')
        if not ne_id or not policy_id:
            return Response(
                {'error': 'ne_id and policy_id are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Placeholder: actual audit logic in Celery task
        audit = ComplianceAudit.objects.create(
            network_element_id=ne_id,
            policy_id=policy_id,
            result=ComplianceAudit.Result.COMPLIANT,
            expected_config={},
            actual_config={},
            deviations=[],
            audited_by=request.user.username,
        )
        return Response(
            ComplianceAuditSerializer(audit).data,
            status=status.HTTP_201_CREATED,
        )


class ConfigurationSnapshotViewSet(viewsets.ModelViewSet):
    """Manage configuration snapshots."""

    queryset = ConfigurationSnapshot.objects.select_related(
        'network_element'
    ).all()
    serializer_class = ConfigurationSnapshotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['network_element', 'snapshot_type']

    @action(detail=False, methods=['post'], url_path='capture')
    def capture_snapshot(self, request):
        """Capture a new configuration snapshot from an NE."""
        ne_id = request.data.get('ne_id')
        snapshot_type = request.data.get(
            'snapshot_type', 'MANUAL'
        )
        if not ne_id:
            return Response(
                {'error': 'ne_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Placeholder: actual SNMP/SSH read in Celery task
        snapshot = ConfigurationSnapshot.objects.create(
            network_element_id=ne_id,
            config_data={'placeholder': True},
            snapshot_type=snapshot_type,
            taken_by=request.user.username,
        )
        return Response(
            ConfigurationSnapshotSerializer(snapshot).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='diff')
    def diff_with_previous(self, request, pk=None):
        """Compare this snapshot with the previous one."""
        current = self.get_object()
        previous = ConfigurationSnapshot.objects.filter(
            network_element=current.network_element,
            taken_at__lt=current.taken_at,
        ).first()
        if not previous:
            return Response(
                {'error': 'No previous snapshot found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'current_id': current.id,
            'previous_id': previous.id,
            'current_snapshot': current.config_data,
            'previous_snapshot': previous.config_data,
        })


class FirmwarePolicyViewSet(viewsets.ModelViewSet):
    """Manage firmware policies per NE type."""

    queryset = FirmwarePolicy.objects.all()
    serializer_class = FirmwarePolicySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ne_type', 'is_mandatory']


class TimingSourcePriorityViewSet(viewsets.ModelViewSet):
    """Manage Zero Trust timing source priorities per NE."""

    queryset = TimingSourcePriority.objects.select_related(
        'network_element'
    ).all()
    serializer_class = TimingSourcePrioritySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['network_element', 'source_type', 'enabled']

    @action(detail=False, methods=['get'], url_path='by-ne/(?P<ne_id>[^/.]+)')
    def by_ne(self, request, ne_id=None):
        """Get ordered timing sources for a specific NE."""
        priorities = self.queryset.filter(
            network_element_id=ne_id, enabled=True
        ).order_by('priority')
        return Response(
            TimingSourcePrioritySerializer(priorities, many=True).data
        )
