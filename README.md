# HealthPilot Cloud API

基于 FastAPI 开发的 HealthPilot 云端 API，支持 APP 完成注册/登录、数据同步、数据备份与知识图谱查询的端云联通。

## 功能特性

1. **账号体系与令牌认证** - JWT Bearer Token 鉴权
2. **数据同步与脱敏处理** - 自动过滤敏感字段 (name, phone, id_card, email)
3. **数据备份** - 按用户拉取历史记录
4. **知识图谱查询** - 基于 Neo4j 的关键词检索

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL (SQLAlchemy ORM)
- **图数据库**: Neo4j
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例配置文件并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的 MySQL 和 Neo4j 连接信息。

### 3. 准备数据库

**MySQL:**
```sql
CREATE DATABASE healthpilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Neo4j:**
确保 Neo4j 服务已启动，并可通过 `bolt://localhost:7687` 访问。

### 4. 启动服务

```bash
# 开发模式 (热重载)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

或者直接运行：
```bash
python -m app.main
```

### 5. 访问 API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 | 否 |
| POST | `/api/v1/auth/login` | 用户登录 | 否 |
| POST | `/api/v1/sync/data` | 数据同步 | Bearer Token |
| GET | `/api/v1/backup/data` | 数据备份 | Bearer Token |
| GET | `/api/v1/kg/query?keyword=xxx` | 知识图谱查询 | Bearer Token |
| GET | `/api/v1/kg/health` | 知识图谱健康检查 | Bearer Token |

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── models.py            # Pydantic & SQLAlchemy 模型
│   ├── database.py          # 数据库连接
│   ├── auth.py              # 认证相关
│   ├── routers/
│   │   ├── auth.py          # 认证路由
│   │   ├── sync.py          # 数据同步路由
│   │   ├── backup.py        # 数据备份路由
│   │   └── kg.py            # 知识图谱路由
│   └── services/
│       └── neo4j_service.py # Neo4j 服务
├── requirements.txt
├── .env.example
└── README.md
```

## 脱敏规则

数据同步时自动过滤以下敏感字段：
- `name` - 姓名
- `phone` - 电话
- `id_card` - 身份证号
- `email` - 邮箱

## 模块类型

支持的数据模块类型：
- `DIET` - 饮食
- `EXERCISE` - 运动
- `SLEEP` - 睡眠
- `INTERVENTION` - 干预

## 示例请求

### 注册
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'
```

### 登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'
```

### 数据同步 (需 Token)
```bash
curl -X POST http://localhost:8000/api/v1/sync/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "module": "DIET",
    "payload": {
      "summary": "早餐记录",
      "calorie": 320,
      "phone": "will_be_removed"
    }
  }'
```

### 数据备份 (需 Token)
```bash
curl http://localhost:8000/api/v1/backup/data \
  -H "Authorization: Bearer <your_token>"
```

### 知识图谱查询 (需 Token)
```bash
curl "http://localhost:8000/api/v1/kg/query?keyword=燕麦" \
  -H "Authorization: Bearer <your_token>"
```
