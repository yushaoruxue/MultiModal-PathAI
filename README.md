# AI赋能职教视频个性化教学系统

## 项目简介

本项目是一个以主动智能补偿为核心的教学视频个性化学习支持系统，通过多模态分析学习者的观看行为，自动识别知识薄弱点并主动推送高质量补偿资源，实现真正意义上的"一人一策"个性化教学。

## 技术栈

### 前端
- Vue.js 3 + TypeScript
- Element Plus
- Pinia
- Video.js

### 后端
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy

### AI引擎
- Python 3.9+
- sentence-transformers
- jieba
- networkx

## 项目结构

```
MultiModal-PathAI/
├── backend/          # 后端服务（FastAPI）
├── frontend/         # 前端应用（Vue.js）
├── algorithm/        # AI算法模块
├── docs/             # 项目文档
└── deployment/        # 部署配置
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd MultiModal-PathAI
```

2. 后端设置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 前端设置
```bash
cd frontend
npm install
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入配置信息
```

5. 运行项目
```bash
# 后端
cd backend
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 文档

- [系统架构设计](docs/系统架构设计.md)
- [数据库设计](docs/数据库设计.md)
- [API接口规范](docs/API接口规范.md)
- [开发规范](docs/开发规范.md)

## 开发规范

请参考 [开发规范文档](docs/开发规范.md)

## 团队成员

- **队长**: 周东吴
- **队员**: 成怡、杨雅娟、张亚鹏、雷宇
- **技术顾问**: 蒋国伟
- **指导老师**: 王海霞

## 许可证

[待定]
