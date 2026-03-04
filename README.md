# 鸣潮排轴工具

> 基于 Vue3 + Django 的鸣潮配队管理工具

## 项目简介

鸣潮游戏配队轴工具，支持配队管理、角色筛选、输出流程记录等功能。

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **样式**: TailwindCSS

### 后端
- **框架**: Django 5.x
- **API**: Django REST Framework

## 项目结构

```
.
├── frontend/                 # Vue3 前端项目
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   └── App.vue         # 根组件
│   ├── public/assets/      # 静态资源
│   │   ├── characters/    # 角色头像
│   │   └── icons/          # 元素/武器图标
│   └── package.json
│
├── backend/                  # Django 后端项目
│   ├── api/                # API 应用
│   └── core/               # 项目配置
│
└── README.md
```

## 快速开始

### 1. 启动后端

```bash
cd backend
python manage.py runserver
```

后端运行在 http://127.0.0.1:8000

### 2. 启动前端

```bash
cd frontend
npm run dev
```

前端运行在 http://localhost:3000

## 功能特性

- 角色筛选（星级、武器、元素）
- 拼音/缩写搜索
- 配队管理（添加、查看）
- 充能需求记录
- DPS/矩阵分数互算（公式：DPS(万) = 矩阵分数 ÷ 1200）
- 适配环境：通用、海虚满协奏
- 夜间模式（默认开启）
- 粉色主题色

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/characters/ | 获取角色列表 |
| GET | /api/filter-options/ | 获取筛选选项 |
| POST | /api/characters/filter/ | 筛选角色 |
| GET | /api/weapons/ | 获取武器列表 |

## 贡献者

- mozz