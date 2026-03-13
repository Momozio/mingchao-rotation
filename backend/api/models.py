from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    """配队表"""

    DIFFICULTY_CHOICES = [
        ("简单", "简单"),
        ("中等", "中等"),
        ("困难", "困难"),
    ]

    name = models.CharField(max_length=100, verbose_name="配队名称")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    axis_length = models.IntegerField(null=True, blank=True, verbose_name="轴长 (秒)")
    dps = models.IntegerField(null=True, blank=True, verbose_name="DPS (万分之一)")
    matrix_score = models.IntegerField(null=True, blank=True, verbose_name="矩阵分数")
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default="中等", verbose_name="难度"
    )
    environment = models.CharField(
        max_length=50, default="通用", verbose_name="适配环境"
    )
    contributors = models.CharField(
        max_length=200, default="mozz", verbose_name="贡献者"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_teams",
        verbose_name="创建者",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "配队"
        verbose_name_plural = "配队"

    def __str__(self):
        return self.name


class TeamCharacter(models.Model):
    """配队角色关联表"""

    team = models.ForeignKey(
        Team,
        related_name="team_characters",
        on_delete=models.CASCADE,
        verbose_name="配队",
    )
    character_id = models.IntegerField(verbose_name="角色 ID")
    character_name = models.CharField(max_length=50, verbose_name="角色名称")
    energy = models.CharField(
        max_length=10, blank=True, default="", verbose_name="充能需求"
    )
    order = models.IntegerField(default=0, verbose_name="顺序")

    class Meta:
        ordering = ["order"]
        verbose_name = "配队角色"
        verbose_name_plural = "配队角色"

    def __str__(self):
        return f"{self.team.name} - {self.character_name}"


class RotationAxis(models.Model):
    """输出轴表"""

    team = models.ForeignKey(
        Team, related_name="axes", on_delete=models.CASCADE, verbose_name="配队"
    )
    name = models.CharField(max_length=100, verbose_name="轴名称")
    video_url = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="视频 URL"
    )
    total_duration = models.IntegerField(default=30, verbose_name="总时长 (秒)")
    segments_data = models.JSONField(default=dict, verbose_name="时间轴数据")
    characters = models.JSONField(default=list, verbose_name="角色列表")
    order = models.IntegerField(default=0, verbose_name="顺序")

    class Meta:
        ordering = ["order"]
        verbose_name = "输出轴"
        verbose_name_plural = "输出轴"

    def __str__(self):
        return f"{self.team.name} - {self.name}"
