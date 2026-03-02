"""
知识图谱查询路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import (
    UserDB,
    KGQueryResponse,
    KGQueryResult,
    ErrorResponse
)
from app.services.neo4j_service import get_neo4j_service, Neo4jService

router = APIRouter(prefix="/kg", tags=["知识图谱"])


@router.get(
    "/query",
    response_model=KGQueryResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        503: {"model": ErrorResponse, "description": "知识图谱服务不可用"}
    },
    summary="知识图谱查询",
    description="按关键词检索知识图谱中的实体"
)
async def query_knowledge_graph(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    知识图谱查询接口
    
    - **keyword**: 搜索关键词 (如: 燕麦、糖尿病等)
    
    返回匹配的实体列表，包含：
    - name: 实体名称
    - labels: 实体标签类型
    - n: 节点的详细属性
    
    **注意**: 需要 Bearer Token 认证
    """
    # 验证 Neo4j 连接
    if not neo4j.verify_connectivity():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="知识图谱服务暂时不可用"
        )
    
    # 执行查询
    results = neo4j.query_by_keyword(keyword)
    
    # 转换为响应模型
    kg_results = [
        KGQueryResult(
            name=r["name"],
            labels=r["labels"],
            n=r["n"]
        )
        for r in results
    ]
    
    return KGQueryResponse(results=kg_results)


@router.get(
    "/health",
    summary="知识图谱服务健康检查",
    description="检查 Neo4j 连接状态"
)
async def kg_health_check(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    知识图谱健康检查接口
    
    返回 Neo4j 连接状态和节点数量
    """
    is_connected = neo4j.verify_connectivity()
    node_count = 0
    
    if is_connected:
        node_count = neo4j.get_node_count()
    
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "connected": is_connected,
        "node_count": node_count
    }
