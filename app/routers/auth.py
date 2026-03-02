"""
认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import create_user, authenticate_user, create_access_token
from app.models import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    ErrorResponse
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=TokenResponse,
    responses={
        400: {"model": ErrorResponse, "description": "用户名已存在"},
        422: {"model": ErrorResponse, "description": "请求参数错误"}
    },
    summary="用户注册",
    description="注册新用户并返回 JWT 令牌"
)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - **username**: 用户名 (3-50字符)
    - **password**: 密码 (至少6字符)
    
    返回 JWT 令牌和过期时间戳
    """
    # 检查用户名是否已存在
    from app.models import UserDB
    existing_user = db.query(UserDB).filter(UserDB.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建用户
    user = create_user(db, request.username, request.password)
    
    # 生成令牌
    token, expires_at = create_access_token(user.username, user.id)
    
    return TokenResponse(token=token, expires_at=expires_at)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "用户名或密码错误"}
    },
    summary="用户登录",
    description="用户登录并返回 JWT 令牌"
)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT 令牌和过期时间戳
    """
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成令牌
    token, expires_at = create_access_token(user.username, user.id)
    
    return TokenResponse(token=token, expires_at=expires_at)
