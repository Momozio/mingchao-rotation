import os
import time
import subprocess
import imageio_ffmpeg


def get_ffmpeg_path():
    return imageio_ffmpeg.get_ffmpeg_exe()


def get_ffprobe_path():
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    return ffmpeg_path.replace("ffmpeg", "ffprobe")


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

# 角色数据
CHARACTERS_DATA = [
    {"id": 1, "name": "丹瑾", "star": 4, "element": "冷凝", "weapon": "迅刀"},
    {"id": 2, "name": "仇远", "star": 5, "element": "导电", "weapon": "佩枪"},
    {"id": 3, "name": "今汐", "star": 5, "element": "热熔", "weapon": "长刃"},
    {"id": 4, "name": "凌阳", "star": 4, "element": "气动", "weapon": "臂铠"},
    {"id": 5, "name": "千咲", "star": 4, "element": "导电", "weapon": "音感仪"},
    {"id": 6, "name": "卜灵", "star": 4, "element": "衍射", "weapon": "音感仪"},
    {"id": 7, "name": "卡卡罗", "star": 5, "element": "导电", "weapon": "迅刀"},
    {"id": 8, "name": "卡提希娅", "star": 5, "element": "湮灭", "weapon": "长刃"},
    {"id": 9, "name": "吟霖", "star": 4, "element": "导电", "weapon": "音感仪"},
    {"id": 10, "name": "嘉贝莉娜", "star": 5, "element": "冷凝", "weapon": "佩枪"},
    {"id": 11, "name": "坎特蕾拉", "star": 5, "element": "湮灭", "weapon": "音感仪"},
    {"id": 12, "name": "夏空", "star": 4, "element": "气动", "weapon": "长刃"},
    {"id": 13, "name": "奥古斯塔", "star": 5, "element": "导电", "weapon": "长刃"},
    {"id": 14, "name": "守岸人", "star": 5, "element": "冷凝", "weapon": "音感仪"},
    {"id": 15, "name": "安可", "star": 4, "element": "热熔", "weapon": "音感仪"},
    {"id": 16, "name": "尤诺", "star": 5, "element": "气动", "weapon": "音感仪"},
    {"id": 17, "name": "布兰特", "star": 4, "element": "热熔", "weapon": "佩枪"},
    {"id": 18, "name": "弗洛洛", "star": 5, "element": "冷凝", "weapon": "长刃"},
    {"id": 19, "name": "忌炎", "star": 5, "element": "气动", "weapon": "长刃"},
    {"id": 20, "name": "折枝", "star": 5, "element": "冷凝", "weapon": "音感仪"},
    {"id": 21, "name": "散华", "star": 4, "element": "冷凝", "weapon": "迅刀"},
    {"id": 22, "name": "桃祈", "star": 4, "element": "气动", "weapon": "长刃"},
    {"id": 23, "name": "椿", "star": 5, "element": "湮灭", "weapon": "迅刀"},
    {"id": 24, "name": "洛可可", "star": 4, "element": "导电", "weapon": "音感仪"},
    {"id": 25, "name": "渊武", "star": 4, "element": "湮灭", "weapon": "臂铠"},
    {"id": 26, "name": "漂泊者·气动", "star": 5, "element": "气动", "weapon": "长刃"},
    {"id": 27, "name": "漂泊者·湮灭", "star": 5, "element": "湮灭", "weapon": "长刃"},
    {"id": 28, "name": "漂泊者·衍射", "star": 5, "element": "衍射", "weapon": "长刃"},
    {"id": 29, "name": "灯灯", "star": 4, "element": "导电", "weapon": "音感仪"},
    {"id": 30, "name": "炽霞", "star": 4, "element": "热熔", "weapon": "佩枪"},
    {"id": 31, "name": "爱弥斯", "star": 4, "element": "衍射", "weapon": "佩枪"},
    {"id": 32, "name": "珂莱塔", "star": 5, "element": "冷凝", "weapon": "佩枪"},
    {"id": 33, "name": "琳奈", "star": 4, "element": "气动", "weapon": "佩枪"},
    {"id": 34, "name": "白芷", "star": 4, "element": "湮灭", "weapon": "音感仪"},
    {"id": 35, "name": "相里要", "star": 5, "element": "导电", "weapon": "臂铠"},
    {"id": 36, "name": "秋水", "star": 4, "element": "湮灭", "weapon": "迅刀"},
    {"id": 37, "name": "秧秧", "star": 4, "element": "气动", "weapon": "迅刀"},
    {"id": 38, "name": "维里奈", "star": 5, "element": "气动", "weapon": "音感仪"},
    {"id": 39, "name": "莫宁", "star": 4, "element": "热熔", "weapon": "长刃"},
    {"id": 40, "name": "莫特斐", "star": 4, "element": "湮灭", "weapon": "音感仪"},
    {"id": 41, "name": "菲比", "star": 5, "element": "衍射", "weapon": "音感仪"},
    {"id": 42, "name": "赞妮", "star": 5, "element": "热熔", "weapon": "佩枪"},
    {"id": 43, "name": "釉瑚", "star": 4, "element": "衍射", "weapon": "音感仪"},
    {"id": 44, "name": "鉴心", "star": 5, "element": "冷凝", "weapon": "臂铠"},
    {"id": 45, "name": "长离", "star": 5, "element": "热熔", "weapon": "迅刀"},
    {"id": 46, "name": "陆·赫斯", "star": 5, "element": "湮灭", "weapon": "佩枪"},
    {"id": 47, "name": "露帕", "star": 4, "element": "热熔", "weapon": "佩枪"},
]


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


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
        return Response({"error": "No video file"}, status=400)

    # 生成时间戳文件名
    timestamp = int(time.time())
    ext = video_file.name.split(".")[-1]
    filename = f"{timestamp}.{ext}"

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
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "28",
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
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "28",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            "-y",
            output_path,
        ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True)
    if result.returncode != 0:
        error_msg = result.stderr.decode() if result.stderr else "Unknown error"
        return Response(
            {"error": f"Video processing failed: {error_msg[:200]}"}, status=500
        )

    # 检查输出文件是否创建成功
    if not os.path.exists(output_path):
        return Response({"error": "Output video file not created"}, status=500)

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
