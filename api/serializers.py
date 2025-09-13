from rest_framework import serializers
from .models import Cat, Mission, Target
import requests

class CatSerializer(serializers.ModelSerializer):
    current_mission = serializers.SerializerMethodField()
    
    class Meta:
        model = Cat
        fields = [
            "id",
            "name",
            "years_of_experience",
            "breed",
            "salary",
            "current_mission",
            "hired_at",
        ]
        read_only_fields = ["hired_at"]

    def get_current_mission(self, obj):
        mission = Mission.objects.filter(assigned_cat=obj, completed=False).first()
        if mission:
            return MissionSerializer(mission).data
        return None

    def validate_breed(self, value):
        try:
            response = requests.get("https://api.thecatapi.com/v1/breeds", timeout=5)
            response.raise_for_status()
            breeds = [breed["name"] for breed in response.json()]
        except requests.RequestException:
            raise serializers.ValidationError(
                "Could not validate breed at this time. Please try again later."
            )

        if value not in breeds:
            raise serializers.ValidationError(
                f"Breed must be one of the valid cat breeds: {', '.join(breeds)}"
            )
        return value


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ["id", "name", "country", "notes", "completed", "completed_at"]
        read_only_fields = ["completed_at"]


class MissionSerializer(serializers.ModelSerializer):
    # nested targets on create/read
    targets = TargetSerializer(many=True)
    assigned_cat = serializers.StringRelatedField()

    class Meta:
        model = Mission
        fields = [
            "id",
            "title",
            "description",
            "assigned_cat",
            "completed",
            "created_at",
            "targets",
        ]
        read_only_fields = ["completed", "created_at"]

    def validate_targets(self, value):
        if not (1 <= len(value) <= 3):
            raise serializers.ValidationError(
                "Mission must include between 1 and 3 targets."
            )
        return value

    def create(self, validated_data):
        targets_data = validated_data.pop("targets")
        mission = Mission.objects.create(**validated_data)
        for t in targets_data:
            Target.objects.create(mission=mission, **t)
        return mission

    def update(self, instance, validated_data):
        # Normally you won’t update targets here (they’re separate endpoints).
        # Just handle mission basic fields.
        validated_data.pop("targets", None)
        return super().update(instance, validated_data)
