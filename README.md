# 游戏攻略网站

> 基于 Vue3 + Django 的前后端分离游戏攻略平台

## 项目简介

一个中等规模的 web 应用，提供游戏攻略浏览、收藏、评论等功能。

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **样式**: TailwindCSS 4.x
- **HTTP**: Fetch API

### 后端
- **框架**: Django 5.x
- **API**: Django REST Framework
- **跨域**: django-cors-headers
- **数据库**: SQLite3 (开发) / PostgreSQL (生产)

## 项目结构

```
.
├── frontend/                 # Vue3 前端项目
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   ├── api/            # API 请求封装
│   │   ├── stores/         # 状态管理
│   │   ├── router/         # 路由配置
│   │   └── App.vue         # 根组件
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/                  # Django 后端项目
│   ├── api/                # API 应用
│   │   ├── models.py       # 数据模型
│   │   ├── views.py        # 视图函数
│   │   ├── serializers.py  # 序列化器
│   │   └── urls.py         # 路由
│   ├── core/               # 项目配置
│   │   ├── settings.py     # Django 配置
│   │   └── urls.py         # 主路由
│   └── manage.py
│
└── README.md
```

## 开发环境要求

- Node.js 18+
- Python 3.10+
- Git

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd mingchao_rotation
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

后端运行在 http://127.0.0.1:8000

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:3000

## 可用的 npm 脚本

- `npm run dev` - 启动开发服务器
- `npm run build` - 构建生产版本
- `npm run preview` - 预览生产版本

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/health/ | 健康检查 |

## 开发规范

### 前端
- 使用 Composition API + `<script setup>`
- 组件文件名使用 PascalCase
- CSS 类名使用 TailwindCSS

### 后端
- 遵循 Django 开发规范
- 使用 DRF 进行 API 开发
- 注意安全配置 (DEBUG=False in production)

## 性能优化 (生产环境)

- 前端: 开启 gzip 压缩、静态资源 CDN
- 后端: 使用 Redis 缓存、数据库索引优化
- 安全: HTTPS、CORS 配置、CSRF 保护

## 许可证

MIT License