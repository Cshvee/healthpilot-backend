"""
数据同步路由 (脱敏处理)
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import (
    UserDB,
    DataRecordDB,
    DataSyncRequest,
    DataSyncResponse,
    ErrorResponse,
    ModuleType
)

router = APIRouter(prefix="/sync", tags=["数据同步"])

# 需要脱敏的敏感字段
SENSITIVE_FIELDS = {"name", "phone", "id_card", "email"}


def desensitize_data(data: dict) -> dict:
    """
    数据脱敏处理
    过滤掉敏感字段: name, phone, id_card, email
    """
    if not isinstance(data, dict):
        return data
    
    return {
        key: value
        for key, value in data.items()
        if key not in SENSITIVE_FIELDS
    }


@router.post(
    "/data",
    response_model=DataSyncResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        422: {"model": ErrorResponse, "description": "请求参数错误"}
    },
    summary="脱敏数据同步",
    description="同步用户数据，自动过滤敏感字段"
)
async def sync_data(
    request: DataSyncRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    数据同步接口
    
    - **module**: 模块类型 (DIET, EXERCISE, SLEEP, INTERVENTION)
    - **payload**: 数据内容 (会自动脱敏)
    
    脱敏规则：过滤 name, phone, id_card, email 字段
    
    **注意**: 需要 Bearer Token 认证
    """
    # 脱敏处理
    filtered_payload = desensitize_data(request.payload)
    
    # 创建数据记录
    record = DataRecordDB(
        user_id=current_user.id,
        module=request.module.value,
        payload=json.dumps(filtered_payload, ensure_ascii=False)
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return DataSyncResponse(
        record_id=record.id,
        created_at=int(record.created_at.timestamp()) if record.created_at else 0
    )
