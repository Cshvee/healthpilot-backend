"""
认证相关功能
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import UserDB, UserInfo

settings = get_settings()
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    password_bytes = password.encode('utf-8')
    # bcrypt 限制密码长度 72 字节
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(username: str, user_id: int) -> tuple[str, int]:
    """
    创建 JWT 访问令牌
    返回: (token, expires_at_timestamp)
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = int(expire.timestamp())
    
    to_encode = {
        "sub": username,
        "user_id": user_id,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, expires_at


def decode_token(token: str) -> Optional[dict]:
    """解码 JWT 令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserDB:
    """
    获取当前用户 (依赖注入用)
    验证 Bearer Token 并返回用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("user_id")
    username = payload.get("sub")
    
    if user_id is None or username is None:
        raise credentials_exception
    
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserDB]:
    """验证用户凭据"""
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, username: str, password: str) -> UserDB:
    """创建新用户"""
    hashed_password = get_password_hash(password)
    db_user = UserDB(
        username=username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def user_to_info(user: UserDB) -> UserInfo:
    """转换用户模型为 UserInfo"""
    return UserInfo(
        id=user.id,
        username=user.username,
        created_at=int(user.created_at.timestamp()) if user.created_at else 0
    )
