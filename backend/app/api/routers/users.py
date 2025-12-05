from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserRead, UserUpdate
from app.models.user import User
from app.deps import get_current_user, get_user_service
from app.services.user_service import UserService, UserAlreadyExists
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    現在のログインユーザーのプロフィール情報を取得します。
    """
    return current_user


@router.patch("/me", response_model=UserRead)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    認証済みユーザーが自身のプロフィール情報を更新します。
    
    更新可能なフィールド:
    - first_name: 名前
    - last_name: 苗字
    - username: ユーザー名（他のユーザーと重複していないこと）
    
    メールアドレスとパスワードは別エンドポイントで変更します。
    """
    try:
        updated_user = user_service.update_user_profile(db, current_user, user_update)
        return updated_user
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

