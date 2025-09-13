from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cat, Mission, Target
from .serializers import CatSerializer, MissionSerializer, TargetSerializer

class CatViewSet(viewsets.ModelViewSet):
    """
    CRUD for spy cats
    """
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

class MissionViewSet(viewsets.ModelViewSet):
    """
    Manage missions (with nested targets).
    """
    queryset = Mission.objects.prefetch_related("targets").all()
    serializer_class = MissionSerializer

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()
        if mission.assigned_cat:
            return Response(
                {"error": "Cannot delete a mission that is already assigned to a cat."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    # Assign a cat to this mission
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        mission = self.get_object()
        cat_id = request.data.get("cat_id")

        if not cat_id:
            return Response(
                {"error": "cat_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cat = Cat.objects.get(id=cat_id)
        except Cat.DoesNotExist:
            return Response(
                {"error": "Cat not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Make sure cat has no other active mission
        if Mission.objects.filter(assigned_cat=cat, completed=False).exclude(
            id=mission.id
        ).exists():
            return Response(
                {"error": "This cat already has an active mission."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mission.assigned_cat = cat
        mission.save(update_fields=["assigned_cat"])
        return Response(self.get_serializer(mission).data)

    # Mark a target complete
    @action(detail=True, methods=["post"], url_path="targets/(?P<target_id>[^/.]+)/complete")
    def complete_target(self, request, pk=None, target_id=None):
        mission = self.get_object()
        try:
            target = mission.targets.get(id=target_id)
        except Target.DoesNotExist:
            return Response(
                {"error": "Target not found for this mission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if target.completed:
            return Response({"detail": "Target already completed."})

        target.completed = True
        target.save()
        return Response(TargetSerializer(target).data)

    # Update notes for a target
    @action(detail=True, methods=["patch"], url_path="targets/(?P<target_id>[^/.]+)/notes")
    def update_notes(self, request, pk=None, target_id=None):
        mission = self.get_object()
        try:
            target = mission.targets.get(id=target_id)
        except Target.DoesNotExist:
            return Response(
                {"error": "Target not found for this mission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if mission.completed or target.completed:
            return Response(
                {"error": "Notes cannot be updated on a completed target or mission."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notes = request.data.get("notes")
        if notes is None:
            return Response(
                {"error": "Field 'notes' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target.notes = notes
        target.save(update_fields=["notes"])
        return Response(TargetSerializer(target).data)
