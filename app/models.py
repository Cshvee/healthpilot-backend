"""
数据模型 (Pydantic & SQLAlchemy)
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# SQLAlchemy 基础
Base = declarative_base()


# ========== 枚举类型 ==========
class ModuleType(str, Enum):
    DIET = "DIET"
    EXERCISE = "EXERCISE"
    SLEEP = "SLEEP"
    INTERVENTION = "INTERVENTION"


# ========== SQLAlchemy 模型 ==========
class UserDB(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    data_records = relationship("DataRecordDB", back_populates="user", cascade="all, delete-orphan")


class DataRecordDB(Base):
    """数据记录数据库模型"""
    __tablename__ = "data_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module = Column(String(20), nullable=False)  # DIET, EXERCISE, SLEEP, INTERVENTION
    payload = Column(Text, nullable=False)  # JSON 字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("UserDB", back_populates="data_records")


# ========== Pydantic 模型 (请求/响应) ==========

# ----- 认证相关 -----
class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """令牌响应"""
    token: str = Field(..., description="JWT 令牌")
    expires_at: int = Field(..., description="过期时间戳")


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    created_at: int
    
    class Config:
        from_attributes = True


# ----- 数据同步相关 -----
class DataSyncRequest(BaseModel):
    """数据同步请求"""
    module: ModuleType = Field(..., description="模块类型")
    payload: Dict[str, Any] = Field(..., description="数据内容")


class DataSyncResponse(BaseModel):
    """数据同步响应"""
    record_id: int = Field(..., description="记录ID")
    created_at: int = Field(..., description="创建时间戳")


# ----- 数据备份相关 -----
class DataBackupItem(BaseModel):
    """数据备份项"""
    module: str = Field(..., description="模块类型")
    payload: Dict[str, Any] = Field(..., description="数据内容")
    created_at: int = Field(..., description="创建时间戳")


class DataBackupResponse(BaseModel):
    """数据备份响应"""
    items: List[DataBackupItem] = Field(default=[], description="数据列表")


# ----- 知识图谱相关 -----
class KGQueryResult(BaseModel):
    """知识图谱查询结果项"""
    name: str = Field(..., description="实体名称")
    labels: List[str] = Field(default=[], description="实体标签")
    n: Optional[Dict[str, Any]] = Field(default=None, description="节点详细信息")


class KGQueryResponse(BaseModel):
    """知识图谱查询响应"""
    results: List[KGQueryResult] = Field(default=[], description="查询结果列表")


# ----- 通用响应 -----
class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str = Field(..., description="错误信息")
