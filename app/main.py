"""
HealthPilot Cloud API
FastAPI 主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import auth, sync, backup, kg
from app.services.neo4j_service import neo4j_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    print(f"[启动] {settings.APP_NAME}")
    
    # 初始化数据库表
    try:
        init_db()
        print("[OK] 数据库初始化完成")
    except Exception as e:
        print(f"[WARN] 数据库初始化失败: {e}")
        print("请确保 MySQL 服务已启动并已创建数据库")
    
    # 验证 Neo4j 连接
    try:
        if neo4j_service.verify_connectivity():
            count = neo4j_service.get_node_count()
            print(f"[OK] Neo4j 连接成功，共 {count} 个节点")
        else:
            print("[WARN] Neo4j 连接失败，知识图谱功能不可用")
    except Exception as e:
        print(f"[WARN] Neo4j 连接错误: {e}")
    
    yield
    
    # 关闭时执行
    print("[关闭] 应用")
    neo4j_service.close()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="HealthPilot 云端 API - 支持 APP 注册/登录、数据同步、数据备份与知识图谱查询",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(sync.router, prefix=settings.API_V1_PREFIX)
app.include_router(backup.router, prefix=settings.API_V1_PREFIX)
app.include_router(kg.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
