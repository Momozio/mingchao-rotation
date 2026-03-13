from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team, TeamCharacter, RotationAxis


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("两次密码不一致")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class TeamCharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamCharacter
        fields = ["id", "character_id", "character_name", "energy", "order"]


class RotationAxisSerializer(serializers.ModelSerializer):
    class Meta:
        model = RotationAxis
        fields = [
            "id",
            "name",
            "video_url",
            "total_duration",
            "segments_data",
            "characters",
            "order",
        ]


class TeamSerializer(serializers.ModelSerializer):
    team_characters = TeamCharacterSerializer(many=True, read_only=False)
    axes = RotationAxisSerializer(many=True, read_only=False)
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "remark",
            "axis_length",
            "dps",
            "matrix_score",
            "difficulty",
            "environment",
            "contributors",
            "team_characters",
            "axes",
            "created_by",
            "created_by_id",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        characters_data = validated_data.pop("team_characters", [])
        axes_data = validated_data.pop("axes", [])
        created_by_id = validated_data.pop("created_by_id", None)

        team = Team.objects.create(**validated_data)

        if created_by_id:
            team.created_by_id = created_by_id
            team.save()

        for char_data in characters_data:
            TeamCharacter.objects.create(team=team, **char_data)

        for axis_data in axes_data:
            RotationAxis.objects.create(team=team, **axis_data)

        return team

    def update(self, instance, validated_data):
        characters_data = validated_data.pop("team_characters", None)
        axes_data = validated_data.pop("axes", None)

        # 更新 Team 基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新角色（删除旧的，创建新的）
        if characters_data is not None:
            instance.team_characters.all().delete()
            for char_data in characters_data:
                TeamCharacter.objects.create(team=instance, **char_data)

        # 更新轴（删除旧的，创建新的）
        if axes_data is not None:
            instance.axes.all().delete()
            for axis_data in axes_data:
                RotationAxis.objects.create(team=instance, **axis_data)

        return instance
