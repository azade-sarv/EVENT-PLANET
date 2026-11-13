from rest_framework import serializers

from .models import Stage, StageRole


class StageSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Stage
        fields = (
            "id",
            "event",
            "title",
            "description",
            "order",
            "start_time",
            "end_time",
            "roles",
        )
        read_only_fields = ("id",)

    def get_roles(self, obj):
        roles = obj.roles.select_related("user").all()
        return [
            {
                "id": role.id,
                "username": role.user.username,
                "role_type": role.role_type,
            }
            for role in roles
        ]

    def validate_event(self, event):
        user = self.context["request"].user
        if event.organizer != user:
            raise serializers.ValidationError(
                "You can only add stages to your own events."
            )
        return event

    def validate(self, attrs):
        event = attrs.get("event")
        order = attrs.get("order")

        qs = Stage.objects.filter(event=event, order=order)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"order": "This order already exists for this event."}
            )

        return attrs


class StageRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = StageRole
        fields = ("id", "stage", "user", "username", "role_type")
        read_only_fields = ("id", "username")

    def validate_stage(self, stage):
        user = self.context["request"].user
        if stage.event.organizer != user:
            raise serializers.ValidationError(
                "You can only manage roles for your own events."
            )
        return stage