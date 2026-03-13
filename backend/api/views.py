import os
import time
import subprocess
import imageio_ffmpeg
from django.http import StreamingHttpResponse, FileResponse, Http404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from .models import Team, TeamCharacter, RotationAxis
from .serializers import TeamSerializer, RegisterSerializer, UserSerializer


def get_ffmpeg_path():
    return imageio_ffmpeg.get_ffmpeg_exe()


def get_ffprobe_path():
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    return ffmpeg_path.replace("ffmpeg", "ffprobe")


def stream_video(request, filename):
    """支持 Range 请求的视频流视图"""
    video_path = os.path.join(settings.MEDIA_ROOT, "videos", filename)

    if not os.path.exists(video_path):
        raise Http404("Video not found")

    file_size = os.path.getsize(video_path)
    range_header = request.META.get("HTTP_RANGE")

    if range_header:
        range_unit, range_spec = range_header.split("=")
        start, end = range_spec.split("-")
        start = int(start) if start else 0
        end = int(end) if end else file_size - 1
        end = min(end, file_size - 1)

        def file_iterator(file_obj, chunk_size=8192):
            file_obj.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = file_obj.read(min(chunk_size, remaining))
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)

        response = StreamingHttpResponse(
            file_iterator(open(video_path, "rb")), content_type="video/mp4", status=206
        )
        response["Content-Length"] = end - start + 1
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response["Accept-Ranges"] = "bytes"
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    else:
        response = FileResponse(open(video_path, "rb"), content_type="video/mp4")
        response["Content-Length"] = file_size
        response["Accept-Ranges"] = "bytes"
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response


# 角色数据
CHARACTERS_DATA = [
    {"id": 1, "name": "漂泊者·衍射", "star": 5, "element": "衍射", "weapon": "迅刀"},
    {"id": 2, "name": "漂泊者·湮灭", "star": 5, "element": "湮灭", "weapon": "迅刀"},
    {"id": 3, "name": "漂泊者·气动", "star": 5, "element": "气动", "weapon": "迅刀"},
    {"id": 4, "name": "安可", "star": 5, "element": "热熔", "weapon": "音感仪"},
    {"id": 5, "name": "维里奈", "star": 5, "element": "衍射", "weapon": "音感仪"},
    {"id": 6, "name": "凌阳", "star": 5, "element": "冷凝", "weapon": "臂铠"},
    {"id": 7, "name": "鉴心", "star": 5, "element": "气动", "weapon": "臂铠"},
    {"id": 8, "name": "卡卡罗", "star": 5, "element": "导电", "weapon": "长刃"},
    {"id": 9, "name": "忌炎", "star": 5, "element": "气动", "weapon": "长刃"},
    {"id": 10, "name": "今汐", "star": 5, "element": "衍射", "weapon": "长刃"},
    {"id": 11, "name": "长离", "star": 5, "element": "热熔", "weapon": "迅刀"},
    {"id": 12, "name": "椿", "star": 5, "element": "湮灭", "weapon": "迅刀"},
    {"id": 13, "name": "相里要", "star": 5, "element": "导电", "weapon": "臂铠"},
    {"id": 14, "name": "守岸人", "star": 5, "element": "衍射", "weapon": "音感仪"},
    {"id": 15, "name": "卡提希娅", "star": 5, "element": "气动", "weapon": "迅刀"},
    {"id": 16, "name": "坎特蕾拉", "star": 5, "element": "湮灭", "weapon": "音感仪"},
    {"id": 17, "name": "珂莱塔", "star": 5, "element": "冷凝", "weapon": "佩枪"},
    {"id": 18, "name": "弗洛洛", "star": 5, "element": "湮灭", "weapon": "音感仪"},
    {"id": 19, "name": "琳奈", "star": 5, "element": "衍射", "weapon": "佩枪"},
    {"id": 20, "name": "莫宁", "star": 5, "element": "热熔", "weapon": "长刃"},
    {"id": 21, "name": "爱弥斯", "star": 5, "element": "热熔", "weapon": "迅刀"},
    {"id": 22, "name": "陆·赫斯", "star": 5, "element": "衍射", "weapon": "臂铠"},
    {"id": 23, "name": "仇远", "star": 5, "element": "气动", "weapon": "迅刀"},
    {"id": 24, "name": "嘉贝莉娜", "star": 5, "element": "热熔", "weapon": "佩枪"},
    {"id": 25, "name": "露帕", "star": 5, "element": "热熔", "weapon": "长刃"},
    {"id": 26, "name": "折枝", "star": 5, "element": "冷凝", "weapon": "音感仪"},
    {"id": 27, "name": "千咲", "star": 5, "element": "湮灭", "weapon": "长刃"},
    {"id": 28, "name": "卜灵", "star": 4, "element": "导电", "weapon": "音感仪"},
    {"id": 29, "name": "吟霖", "star": 5, "element": "导电", "weapon": "音感仪"},
    {"id": 30, "name": "夏空", "star": 5, "element": "气动", "weapon": "佩枪"},
    {"id": 31, "name": "奥古斯塔", "star": 5, "element": "导电", "weapon": "长刃"},
    {"id": 32, "name": "尤诺", "star": 5, "element": "气动", "weapon": "臂铠"},
    {"id": 33, "name": "布兰特", "star": 5, "element": "热熔", "weapon": "迅刀"},
    {"id": 34, "name": "洛可可", "star": 5, "element": "湮灭", "weapon": "臂铠"},
    {"id": 35, "name": "菲比", "star": 5, "element": "衍射", "weapon": "音感仪"},
    {"id": 36, "name": "赞妮", "star": 5, "element": "衍射", "weapon": "臂铠"},
    {"id": 37, "name": "秧秧", "star": 4, "element": "气动", "weapon": "迅刀"},
    {"id": 38, "name": "白芷", "star": 4, "element": "冷凝", "weapon": "音感仪"},
    {"id": 39, "name": "炽霞", "star": 4, "element": "热熔", "weapon": "佩枪"},
    {"id": 40, "name": "散华", "star": 4, "element": "冷凝", "weapon": "迅刀"},
    {"id": 41, "name": "秋水", "star": 4, "element": "气动", "weapon": "佩枪"},
    {"id": 42, "name": "丹瑾", "star": 4, "element": "湮灭", "weapon": "迅刀"},
    {"id": 43, "name": "莫特斐", "star": 4, "element": "热熔", "weapon": "佩枪"},
    {"id": 44, "name": "渊武", "star": 4, "element": "导电", "weapon": "臂铠"},
    {"id": 45, "name": "桃祈", "star": 4, "element": "湮灭", "weapon": "长刃"},
    {"id": 46, "name": "灯灯", "star": 4, "element": "导电", "weapon": "长刃"},
    {"id": 47, "name": "釉瑚", "star": 4, "element": "冷凝", "weapon": "臂铠"},
]


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username, "message": "注册成功"},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {"id": self.user.id, "username": self.user.username}
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_current_user(request):
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({"detail": "未登录"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def get_characters(request):
    return Response(CHARACTERS_DATA)


@api_view(["GET"])
def get_weapons(request):
    weapons = ["佩枪", "迅刀", "长刃", "音感仪", "臂铠"]
    return Response(weapons)


@api_view(["GET"])
def get_filter_options(request):
    stars = [4, 5]
    weapons = ["佩枪", "迅刀", "长刃", "音感仪", "臂铠"]
    elements = ["冷凝", "导电", "气动", "湮灭", "热熔", "衍射"]
    return Response({"stars": stars, "weapons": weapons, "elements": elements})


@api_view(["POST"])
def filter_characters(request):
    data = request.data
    result = CHARACTERS_DATA

    if data.get("stars"):
        result = [c for c in result if c["star"] in data["stars"]]
    if data.get("weapons"):
        result = [c for c in result if c["weapon"] in data["weapons"]]
    if data.get("elements"):
        result = [c for c in result if c["element"] in data["elements"]]
    if data.get("search"):
        search = data["search"].lower()
        result = [c for c in result if search in c["name"].lower()]

    return Response(result)


@api_view(["POST"])
def upload_video(request):
    video_file = request.FILES.get("video")
    if not video_file:
        return Response({"error": "没有视频文件"}, status=400)

    # 限制文件大小 500MB - 在上传前就检查
    max_size = 500 * 1024 * 1024
    file_size_mb = video_file.size / 1024 / 1024
    print(f"[INFO] 上传视频：{video_file.name}, 大小：{file_size_mb:.2f}MB")

    if video_file.size > max_size:
        error_msg = f"视频文件过大 ({file_size_mb:.1f}MB)，最大支持 500MB"
        print(f"[ERROR] {error_msg}")
        return Response({"error": error_msg}, status=400)

    # 生成时间戳文件名
    timestamp = int(time.time())
    ext = video_file.name.split(".")[-1]
    filename = f"{timestamp}.mp4"  # 统一输出 mp4 格式

    # 保存上传的原始视频
    upload_dir = os.path.join(settings.MEDIA_ROOT, "videos")
    os.makedirs(upload_dir, exist_ok=True)
    original_path = os.path.join(upload_dir, f"original_{filename}")

    with open(original_path, "wb+") as f:
        for chunk in video_file.chunks():
            f.write(chunk)

    # 检查是否有裁剪参数
    start_time = request.POST.get("start_time", None)
    duration = request.POST.get("duration", None)

    # 确定处理的最终输出路径
    output_path = os.path.join(upload_dir, filename)

    # 720p 压缩参数
    # CRF 23-28: 数值越大压缩越强，28 适合网络传输
    # preset medium: 平衡速度和质量
    # maxrate/bufsize: 限制码率避免过大
    if start_time is not None and duration is not None:
        # 执行带时间裁剪的转换
        ffmpeg_cmd = [
            get_ffmpeg_path(),
            "-ss",
            str(start_time),
            "-t",
            str(duration),
            "-i",
            original_path,
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "26",  # 稍微提高质量，26 比 28 更清晰
            "-maxrate",
            "2500k",  # 最大码率 2.5Mbps
            "-bufsize",
            "5000k",  # 缓冲区大小 5Mbps
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            "-y",
            output_path,
        ]
    else:
        ffmpeg_cmd = [
            get_ffmpeg_path(),
            "-i",
            original_path,
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "26",
            "-maxrate",
            "2500k",
            "-bufsize",
            "5000k",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            "-y",
            output_path,
        ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, timeout=300)
    if result.returncode != 0:
        error_msg = result.stderr.decode() if result.stderr else "Unknown error"
        print(f"[ERROR] FFmpeg 处理失败：{error_msg[:500]}")
        return Response({"error": f"视频处理失败：{error_msg[:200]}"}, status=500)

    print(f"[SUCCESS] 视频处理完成：{output_path}")
    print(f"[INFO] 输出文件大小：{os.path.getsize(output_path) / 1024 / 1024:.2f}MB")

    # 检查输出文件是否创建成功
    if not os.path.exists(output_path):
        return Response({"error": "输出视频文件创建失败"}, status=500)

    # 检查输出文件大小，如果超过 100MB 则重新压缩
    output_size = os.path.getsize(output_path)
    if output_size > 100 * 1024 * 1024:
        # 重新压缩，使用更高的压缩率
        recompressed_path = os.path.join(upload_dir, f"recompressed_{filename}")
        ffmpeg_cmd = [
            get_ffmpeg_path(),
            "-i",
            output_path,
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "28",
            "-maxrate",
            "1500k",
            "-bufsize",
            "3000k",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            "-y",
            recompressed_path,
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True, timeout=300)
        if result.returncode == 0 and os.path.exists(recompressed_path):
            os.remove(output_path)
            os.rename(recompressed_path, output_path)

    # 删除原始文件
    if os.path.exists(original_path):
        os.remove(original_path)

    # 获取视频时长
    duration_cmd = [
        get_ffprobe_path(),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        output_path,
    ]
    try:
        duration_result = subprocess.check_output(duration_cmd).decode().strip()
        duration = float(duration_result)
    except:
        duration = 0.0  # 以防 ffprobe 失败

    video_url = f"{settings.MEDIA_URL}videos/{filename}"
    return Response({"url": video_url, "duration": duration})


class TeamViewSet(viewsets.ModelViewSet):
    """配队 CRUD 视图集"""

    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """支持筛选"""
        queryset = Team.objects.all().select_related("created_by")

        # 创建者筛选（我的配队）
        created_by = self.request.query_params.get("created_by", None)
        if created_by:
            queryset = queryset.filter(created_by_id=int(created_by))

        # 环境筛选
        environment = self.request.query_params.get("environment", None)
        if environment:
            queryset = queryset.filter(environment=environment)

        # 难度筛选
        difficulty = self.request.query_params.get("difficulty", None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # 贡献者筛选
        contributors = self.request.query_params.get("contributors", None)
        if contributors:
            queryset = queryset.filter(contributors__icontains=contributors)

        # 角色筛选（需要包含所有选中的角色）
        character_ids = self.request.query_params.get("character_ids", None)
        if character_ids:
            char_id_list = [int(x) for x in character_ids.split(",")]
            for char_id in char_id_list:
                queryset = queryset.filter(team_characters__character_id=char_id)
            queryset = queryset.distinct()

        # 搜索
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(remark__icontains=search)
                | Q(contributors__icontains=search)
                | Q(code__iexact=search)
            )

        return queryset

    def perform_create(self, serializer):
        """创建时自动设置创建者"""
        if self.request.user.is_authenticated:
            serializer.save(created_by_id=self.request.user.id)
        else:
            raise PermissionDenied("未登录用户无法创建配队")

    def perform_update(self, serializer):
        """更新时检查权限"""
        instance = self.get_object()
        if (
            self.request.user.is_authenticated
            and instance.created_by != self.request.user
        ):
            raise PermissionDenied("只能修改自己的配队")
        serializer.save()

    def perform_destroy(self, instance):
        """删除时检查权限"""
        if (
            self.request.user.is_authenticated
            and instance.created_by != self.request.user
        ):
            raise PermissionDenied("只能删除自己的配队")
        instance.delete()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
