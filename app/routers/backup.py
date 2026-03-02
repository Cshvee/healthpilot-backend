"""
数据备份路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import (
    UserDB,
    DataRecordDB,
    DataBackupResponse,
    DataBackupItem,
    ErrorResponse
)

router = APIRouter(prefix="/backup", tags=["数据备份"])


@router.get(
    "/data",
    response_model=DataBackupResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"}
    },
    summary="脱敏数据备份",
    description="获取用户的历史数据记录（已脱敏）"
)
async def backup_data(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    数据备份接口
    
    返回当前用户的所有历史数据记录
    
    **注意**: 需要 Bearer Token 认证
    """
    # 查询用户的所有数据记录
    records = db.query(DataRecordDB).filter(
        DataRecordDB.user_id == current_user.id
    ).order_by(DataRecordDB.created_at.desc()).all()
    
    items = []
    for record in records:
        try:
            payload = json.loads(record.payload)
        except json.JSONDecodeError:
            payload = {}
        
        items.append(DataBackupItem(
            module=record.module,
            payload=payload,
            created_at=int(record.created_at.timestamp()) if record.created_at else 0
        ))
    
    return DataBackupResponse(items=items)
