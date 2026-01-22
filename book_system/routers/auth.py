from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User
from security import get_password_hash, verify_password, create_access_token
from dependencies import get_current_user
from schemas import UserCreate, Token, StandardResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=StandardResponse[User])
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已被注册")
    #test
    print(f"pwd{user_in.password},length{len(user_in.password)}")
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        hashed_password=hashed_pwd
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return StandardResponse(data=new_user)

@router.post("/login", response_model=StandardResponse[Token])
def login(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_in.username)).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user.username})
    token_obj = Token(access_token=access_token, token_type="bearer")

    return StandardResponse(data=token_obj)

@router.get("/me", response_model=StandardResponse[User])
def read_users_me(current_user: User = Depends(get_current_user)):
    return StandardResponse(data=current_user)