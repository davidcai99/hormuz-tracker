# 霍尔木兹海峡船只追踪器

🏛️ 实时追踪霍尔木兹海峡船只数量数据展示平台

## 功能特性

- ✅ **实时数据展示** - 显示已通过和待通过船只数量
- 📊 **数据对比图表** - 柱状图对比实时数据
- 📈 **历史趋势** - 折线图展示14天历史趋势
- 👥 **访问统计** - 按IP统计独立访客数
- 🔄 **自动更新** - 每6小时自动抓取最新数据
- 📱 **响应式设计** - 支持手机和电脑访问

## 项目结构

```
hormuz-tracker/
├── backend/
│   ├── app.py           # Flask 后端服务
│   ├── scraper.py       # 数据抓取脚本
│   ├── models.py        # 数据库模型
│   └── requirements.txt # Python 依赖
├── frontend/
│   ├── index.html       # 主页面
│   ├── styles.css       # 样式表
│   └── app.js           # 前端脚本
├── database/
│   └── ships.db         # SQLite 数据库（自动创建）
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据源（可选）

EIA API Key（免费）: https://www.eia.gov/opendata/

在 `scraper.py` 中填入你的 API Key:
```python
EIA_API_KEY = 'your_api_key_here'
```

### 3. 运行服务

```bash
cd backend
python app.py
```

访问 http://localhost:5000 查看网站

## 部署到 GitHub Pages

这个项目可以部署到 GitHub Pages，但需要额外的静态文件服务器。

### 方案一: GitHub Pages + 外部API

1. 将 `frontend/` 目录内容推送到 `gh-pages` 分支
2. 使用 Railway/Render 部署后端
3. 修改前端 API 地址

### 方案二: Vercel/Netlify

1. 将整个项目推送到 GitHub
2. 连接 Vercel/Netlify
3. 配置构建命令和输出目录

## 数据来源

- **EIA（美国能源信息署）** - 石油运输数据
- **新闻媒体抓取** - Reuters、Maritime Executive 等
- **模拟数据** - 当无真实数据源时使用

## 技术栈

- **后端**: Flask, SQLite, APScheduler
- **前端**: HTML5, CSS3, JavaScript, Chart.js
- **数据库**: SQLite

## 许可证

MIT License
