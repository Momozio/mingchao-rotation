from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

CHARACTERS = [
    {
        "id": 1102,
        "name": "散华",
        "star": 4,
        "weapon": "迅刀",
        "element": "冷凝",
        "pinyin": "sanhua",
        "abbr": "sh",
    },
    {
        "id": 1103,
        "name": "白芷",
        "star": 4,
        "weapon": "音感仪",
        "element": "冷凝",
        "pinyin": "baizhi",
        "abbr": "bz",
    },
    {
        "id": 1104,
        "name": "凌阳",
        "star": 5,
        "weapon": "臂铠",
        "element": "冷凝",
        "pinyin": "lingyang",
        "abbr": "ly",
    },
    {
        "id": 1105,
        "name": "折枝",
        "star": 5,
        "weapon": "音感仪",
        "element": "冷凝",
        "pinyin": "zhizhi",
        "abbr": "zz",
    },
    {
        "id": 1106,
        "name": "釉瑚",
        "star": 4,
        "weapon": "臂铠",
        "element": "冷凝",
        "pinyin": "youhu",
        "abbr": "yh",
    },
    {
        "id": 1107,
        "name": "珂莱塔",
        "star": 5,
        "weapon": "佩枪",
        "element": "冷凝",
        "pinyin": "kelaita",
        "abbr": "klt",
    },
    {
        "id": 1202,
        "name": "炽霞",
        "star": 4,
        "weapon": "佩枪",
        "element": "热熔",
        "pinyin": "chixia",
        "abbr": "cx",
    },
    {
        "id": 1203,
        "name": "安可",
        "star": 5,
        "weapon": "音感仪",
        "element": "热熔",
        "pinyin": "anke",
        "abbr": "ak",
    },
    {
        "id": 1204,
        "name": "莫特斐",
        "star": 4,
        "weapon": "佩枪",
        "element": "热熔",
        "pinyin": "motefei",
        "abbr": "mtf",
    },
    {
        "id": 1205,
        "name": "长离",
        "star": 5,
        "weapon": "迅刀",
        "element": "热熔",
        "pinyin": "changli",
        "abbr": "cl",
    },
    {
        "id": 1206,
        "name": "布兰特",
        "star": 5,
        "weapon": "迅刀",
        "element": "热熔",
        "pinyin": "bulante",
        "abbr": "blt",
    },
    {
        "id": 1207,
        "name": "露帕",
        "star": 5,
        "weapon": "长刃",
        "element": "热熔",
        "pinyin": "lupa",
        "abbr": "lp",
    },
    {
        "id": 1208,
        "name": "嘉贝莉娜",
        "star": 5,
        "weapon": "佩枪",
        "element": "热熔",
        "pinyin": "jiabeilinal",
        "abbr": "jbln",
    },
    {
        "id": 1209,
        "name": "莫宁",
        "star": 5,
        "weapon": "长刃",
        "element": "热熔",
        "pinyin": "monning",
        "abbr": "mn",
    },
    {
        "id": 1210,
        "name": "爱弥斯",
        "star": 5,
        "weapon": "迅刀",
        "element": "热熔",
        "pinyin": "aimisi",
        "abbr": "ams",
    },
    {
        "id": 1301,
        "name": "卡卡罗",
        "star": 5,
        "weapon": "长刃",
        "element": "导电",
        "pinyin": "kakaluo",
        "abbr": "kkl",
    },
    {
        "id": 1302,
        "name": "吟霖",
        "star": 5,
        "weapon": "音感仪",
        "element": "导电",
        "pinyin": "yinlin",
        "abbr": "yl",
    },
    {
        "id": 1303,
        "name": "渊武",
        "star": 4,
        "weapon": "臂铠",
        "element": "导电",
        "pinyin": "yuanwu",
        "abbr": "yw",
    },
    {
        "id": 1304,
        "name": "今汐",
        "star": 5,
        "weapon": "长刃",
        "element": "衍射",
        "pinyin": "jinxi",
        "abbr": "jx",
    },
    {
        "id": 1305,
        "name": "相里要",
        "star": 5,
        "weapon": "臂铠",
        "element": "导电",
        "pinyin": "xiangliyao",
        "abbr": "xly",
    },
    {
        "id": 1306,
        "name": "奥古斯塔",
        "star": 5,
        "weapon": "长刃",
        "element": "导电",
        "pinyin": "aogusita",
        "abbr": "ags",
    },
    {
        "id": 1307,
        "name": "卜灵",
        "star": 4,
        "weapon": "音感仪",
        "element": "导电",
        "pinyin": "buling",
        "abbr": "bl",
    },
    {
        "id": 1402,
        "name": "秧秧",
        "star": 4,
        "weapon": "迅刀",
        "element": "气动",
        "pinyin": "yangyang",
        "abbr": "yy",
    },
    {
        "id": 1403,
        "name": "秋水",
        "star": 4,
        "weapon": "佩枪",
        "element": "气动",
        "pinyin": "qiushui",
        "abbr": "qs",
    },
    {
        "id": 1404,
        "name": "忌炎",
        "star": 5,
        "weapon": "长刃",
        "element": "气动",
        "pinyin": "jiyan",
        "abbr": "jy",
    },
    {
        "id": 1405,
        "name": "鉴心",
        "star": 5,
        "weapon": "臂铠",
        "element": "气动",
        "pinyin": "jianxin",
        "abbr": "jx",
    },
    {
        "id": 1406,
        "name": "漂泊者·气动",
        "star": 5,
        "weapon": "迅刀",
        "element": "气动",
        "pinyin": "piaobozhe",
        "abbr": "pbz",
    },
    {
        "id": 1407,
        "name": "夏空",
        "star": 5,
        "weapon": "佩枪",
        "element": "气动",
        "pinyin": "xiakong",
        "abbr": "xk",
    },
    {
        "id": 1409,
        "name": "卡提希娅",
        "star": 5,
        "weapon": "迅刀",
        "element": "气动",
        "pinyin": "katixiya",
        "abbr": "ktxy",
    },
    {
        "id": 1410,
        "name": "尤诺",
        "star": 5,
        "weapon": "臂铠",
        "element": "气动",
        "pinyin": "yunuo",
        "abbr": "yn",
    },
    {
        "id": 1411,
        "name": "仇远",
        "star": 5,
        "weapon": "迅刀",
        "element": "气动",
        "pinyin": "qiuayuan",
        "abbr": "qy",
    },
    {
        "id": 1501,
        "name": "漂泊者·衍射",
        "star": 5,
        "weapon": "迅刀",
        "element": "衍射",
        "pinyin": "piaobozhe",
        "abbr": "pbz",
    },
    {
        "id": 1503,
        "name": "维里奈",
        "star": 5,
        "weapon": "音感仪",
        "element": "衍射",
        "pinyin": "weilINai",
        "abbr": "wln",
    },
    {
        "id": 1504,
        "name": "灯灯",
        "star": 4,
        "weapon": "长刃",
        "element": "导电",
        "pinyin": "dengdeng",
        "abbr": "dd",
    },
    {
        "id": 1505,
        "name": "守岸人",
        "star": 5,
        "weapon": "音感仪",
        "element": "衍射",
        "pinyin": "shouanren",
        "abbr": "sar",
    },
    {
        "id": 1506,
        "name": "菲比",
        "star": 5,
        "weapon": "音感仪",
        "element": "衍射",
        "pinyin": "feibi",
        "abbr": "fb",
    },
    {
        "id": 1507,
        "name": "赞妮",
        "star": 5,
        "weapon": "臂铠",
        "element": "衍射",
        "pinyin": "zhanni",
        "abbr": "zn",
    },
    {
        "id": 1508,
        "name": "千咲",
        "star": 5,
        "weapon": "长刃",
        "element": "湮灭",
        "pinyin": "qianxiao",
        "abbr": "qx",
    },
    {
        "id": 1509,
        "name": "琳奈",
        "star": 5,
        "weapon": "佩枪",
        "element": "衍射",
        "pinyin": "linnai",
        "abbr": "ln",
    },
    {
        "id": 1510,
        "name": "陆·赫斯",
        "star": 5,
        "weapon": "臂铠",
        "element": "衍射",
        "pinyin": "luhesi",
        "abbr": "lhs",
    },
    {
        "id": 1601,
        "name": "桃祈",
        "star": 4,
        "weapon": "长刃",
        "element": "湮灭",
        "pinyin": "taoqi",
        "abbr": "tq",
    },
    {
        "id": 1602,
        "name": "丹瑾",
        "star": 4,
        "weapon": "迅刀",
        "element": "湮灭",
        "pinyin": "danjin",
        "abbr": "dj",
    },
    {
        "id": 1603,
        "name": "椿",
        "star": 5,
        "weapon": "迅刀",
        "element": "湮灭",
        "pinyin": "chun",
        "abbr": "c",
    },
    {
        "id": 1604,
        "name": "漂泊者·湮灭",
        "star": 5,
        "weapon": "迅刀",
        "element": "湮灭",
        "pinyin": "piaobozhe",
        "abbr": "pbz",
    },
    {
        "id": 1606,
        "name": "洛可可",
        "star": 5,
        "weapon": "臂铠",
        "element": "湮灭",
        "pinyin": "luokeke",
        "abbr": "lkk",
    },
    {
        "id": 1607,
        "name": "坎特蕾拉",
        "star": 5,
        "weapon": "音感仪",
        "element": "湮灭",
        "pinyin": "kanteleila",
        "abbr": "ktll",
    },
    {
        "id": 1608,
        "name": "弗洛洛",
        "star": 5,
        "weapon": "音感仪",
        "element": "湮灭",
        "pinyin": "fuluoluo",
        "abbr": "fll",
    },
]

seen = set()
unique_characters = []
for c in CHARACTERS:
    if c["name"] not in seen:
        seen.add(c["name"])
        unique_characters.append(c)

unique_characters.sort(key=lambda x: (-x["star"], x["name"]))
CHARACTERS = unique_characters

WEAPONS = [
    {"id": 21040056, "name": "白昼之脊", "star": 5, "type": "臂铠"},
    {"id": 21040026, "name": "悲喜剧", "star": 5, "type": "臂铠"},
    {"id": 21050045, "name": "玻色星仪", "star": 5, "type": "音感仪"},
    {"id": 21020036, "name": "不灭航路", "star": 5, "type": "迅刀"},
    {"id": 21020056, "name": "不屈命定之冠", "star": 5, "type": "迅刀"},
    {"id": 21020026, "name": "裁春", "star": 5, "type": "迅刀"},
    {"id": 21020066, "name": "裁竹", "star": 5, "type": "迅刀"},
    {"id": 21010016, "name": "苍鳞千嶂", "star": 5, "type": "长刃"},
    {"id": 21050016, "name": "掣傀之手", "star": 5, "type": "音感仪"},
    {"id": 21030036, "name": "光影双生", "star": 5, "type": "佩枪"},
    {"id": 21050056, "name": "海的呢喃", "star": 5, "type": "音感仪"},
    {"id": 21010015, "name": "浩境粼光", "star": 5, "type": "长刃"},
    {"id": 21050046, "name": "和光回唱", "star": 5, "type": "音感仪"},
    {"id": 21020016, "name": "赫奕流明", "star": 5, "type": "迅刀"},
    {"id": 21020045, "name": "镭射切变", "star": 5, "type": "迅刀"},
    {"id": 21030026, "name": "林间的咏叹调", "star": 5, "type": "佩枪"},
    {"id": 21040045, "name": "脉冲协臂", "star": 5, "type": "臂铠"},
    {"id": 21020015, "name": "千古洑流", "star": 5, "type": "迅刀"},
    {"id": 21040015, "name": "擎渊怒涛", "star": 5, "type": "臂铠"},
    {"id": 21050026, "name": "琼枝冰绡", "star": 5, "type": "音感仪"},
    {"id": 21010026, "name": "时和岁稔", "star": 5, "type": "长刃"},
    {"id": 21030016, "name": "死与舞", "star": 5, "type": "佩枪"},
    {"id": 21010056, "name": "昙切", "star": 5, "type": "长刃"},
    {"id": 21030015, "name": "停驻之烟", "star": 5, "type": "佩枪"},
    {"id": 21040046, "name": "万物持存的注释", "star": 5, "type": "臂铠"},
    {"id": 21030045, "name": "相位涟漪", "star": 5, "type": "佩枪"},
    {"id": 21050036, "name": "星序协响", "star": 5, "type": "音感仪"},
    {"id": 21020046, "name": "血誓盟约", "star": 5, "type": "迅刀"},
    {"id": 21040036, "name": "焰光裁定", "star": 5, "type": "臂铠"},
    {"id": 21010036, "name": "焰痕", "star": 5, "type": "长刃"},
    {"id": 21050015, "name": "漪澜浮录", "star": 5, "type": "音感仪"},
    {"id": 21030046, "name": "溢彩荧辉", "star": 5, "type": "佩枪"},
    {"id": 21020076, "name": "永远的启明星", "star": 5, "type": "迅刀"},
    {"id": 21050066, "name": "幽冥的忘忧章", "star": 5, "type": "音感仪"},
    {"id": 21010046, "name": "驭冕铸雷之权", "star": 5, "type": "长刃"},
    {"id": 21010045, "name": "源能机锋", "star": 5, "type": "长刃"},
    {"id": 21010066, "name": "宙算仪轨", "star": 5, "type": "长刃"},
    {"id": 21040016, "name": "诸方玄枢", "star": 5, "type": "臂铠"},
    {"id": 21040084, "name": "尘云旋臂", "star": 4, "type": "臂铠"},
    {"id": 21040074, "name": "金掌", "star": 4, "type": "臂铠"},
    {"id": 21040094, "name": "酩酊的英雄志", "star": 4, "type": "臂铠"},
    {"id": 21040064, "name": "骇行", "star": 4, "type": "臂铠"},
    {"id": 21040044, "name": "袍泽之固", "star": 4, "type": "臂铠"},
    {"id": 21050084, "name": "核熔星盘", "star": 4, "type": "音感仪"},
    {"id": 21050074, "name": "清音", "star": 4, "type": "音感仪"},
    {"id": 21050094, "name": "虚饰的华尔兹", "star": 4, "type": "音感仪"},
    {"id": 21050044, "name": "今州守望", "star": 4, "type": "音感仪"},
    {"id": 21050064, "name": "异度", "star": 4, "type": "音感仪"},
    {"id": 21030084, "name": "悖论喷流", "star": 4, "type": "佩枪"},
    {"id": 21030074, "name": "奔雷", "star": 4, "type": "佩枪"},
    {"id": 21030064, "name": "飞逝", "star": 4, "type": "佩枪"},
    {"id": 21030044, "name": "无眠烈火", "star": 4, "type": "佩枪"},
    {"id": 21030094, "name": "叙别的罗曼史", "star": 4, "type": "佩枪"},
    {"id": 21030104, "name": "阳焰", "star": 4, "type": "佩枪"},
    {"id": 21020084, "name": "不归孤军", "star": 4, "type": "迅刀"},
    {"id": 21020074, "name": "飞景", "star": 4, "type": "迅刀"},
    {"id": 21020094, "name": "风流的寓言诗", "star": 4, "type": "迅刀"},
    {"id": 21020064, "name": "西升", "star": 4, "type": "迅刀"},
    {"id": 21020104, "name": "翼锋", "star": 4, "type": "迅刀"},
    {"id": 21020044, "name": "永续坍缩", "star": 4, "type": "迅刀"},
    {"id": 21010084, "name": "凋亡频移", "star": 4, "type": "长刃"},
    {"id": 21010064, "name": "东落", "star": 4, "type": "长刃"},
    {"id": 21010094, "name": "容赦的沉思录", "star": 4, "type": "长刃"},
    {"id": 21010024, "name": "异响空灵", "star": 4, "type": "长刃"},
    {"id": 21010044, "name": "永夜长明", "star": 4, "type": "长刃"},
    {"id": 21010074, "name": "纹秋", "star": 4, "type": "长刃"},
    {"id": 21010104, "name": "金穹", "star": 4, "type": "长刃"},
    {"id": 21010034, "name": "重破刃-41型", "star": 4, "type": "长刃"},
    {"id": 21040024, "name": "呼啸重音", "star": 4, "type": "臂铠"},
    {"id": 21040034, "name": "钢影拳-21丁型", "star": 4, "type": "臂铠"},
    {"id": 21040104, "name": "凌空", "star": 4, "type": "臂铠"},
    {"id": 21050024, "name": "鸣动仪-25型", "star": 4, "type": "音感仪"},
    {"id": 21050034, "name": "鸣动仪-25型", "star": 4, "type": "音感仪"},
    {"id": 21050027, "name": "大海的馈赠", "star": 4, "type": "音感仪"},
    {"id": 21050017, "name": "渊海回声", "star": 4, "type": "音感仪"},
    {"id": 21030024, "name": "华彩乐段", "star": 4, "type": "佩枪"},
    {"id": 21030034, "name": "穿击枪-26型", "star": 4, "type": "佩枪"},
    {"id": 21020024, "name": "行进序曲", "star": 4, "type": "迅刀"},
    {"id": 21020034, "name": "瞬斩刀-18型", "star": 4, "type": "迅刀"},
    {"id": 21020017, "name": "心之锚", "star": 4, "type": "迅刀"},
]


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "message": "API is running"})


@api_view(["GET"])
def get_characters(request):
    return Response(CHARACTERS)


@api_view(["GET"])
def get_weapons(request):
    weapon_type = request.GET.get("type")
    star = request.GET.get("star")

    filtered_weapons = WEAPONS

    if weapon_type:
        filtered_weapons = [w for w in filtered_weapons if w["type"] == weapon_type]
    if star:
        filtered_weapons = [w for w in filtered_weapons if w["star"] == int(star)]

    return Response(filtered_weapons)


@api_view(["GET"])
def get_filter_options(request):
    stars = sorted(set(c["star"] for c in CHARACTERS), reverse=True)
    weapons = sorted(set(c["weapon"] for c in CHARACTERS))
    elements = sorted(set(c["element"] for c in CHARACTERS))
    weapon_types = sorted(set(w["type"] for w in WEAPONS))

    return Response(
        {
            "stars": stars,
            "weapons": weapons,
            "elements": elements,
            "weaponTypes": weapon_types,
        }
    )


@api_view(["POST"])
def filter_characters(request):
    data = request.data
    stars = data.get("stars", [])
    weapons = data.get("weapons", [])
    elements = data.get("elements", [])
    search = data.get("search", "").lower()

    filtered = CHARACTERS

    if stars:
        filtered = [c for c in filtered if c["star"] in stars]
    if weapons:
        filtered = [c for c in filtered if c["weapon"] in weapons]
    if elements:
        filtered = [c for c in filtered if c["element"] in elements]
    if search:
        filtered = [
            c
            for c in filtered
            if search in c["name"].lower()
            or search in c.get("pinyin", "").lower()
            or search in c.get("abbr", "").lower()
        ]

    return Response(filtered)
