from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import date, datetime, timedelta
from jose import jwt, JWTError

from myapi import MyAPI
import models
from database import engine, get_db

SECRET_KEY = 'klllllaaaaa--aasdadda'
ALGORITHM = 'HS256'

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
app = MyAPI()

router = app.api_router('auth')

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if user:
        if verify_password(password, user.hashed_password):
            return user
    return False

def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise get_user_exception()
        return {'username': username, 'user_id': user_id}
    except JWTError:
        raise get_user_exception()

@router.post('/create/user')
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.username == create_user.username).first()
    if user:
        app.error(415, "User already exists")
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.username = create_user.username
    create_user_model.hashed_password = get_password_hash(create_user.password)
    create_user_model.is_active = True
    
    db.add(create_user_model)
    db.commit()
    
    return app.success(message='Create user successfully')

@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user:
        token_expires = timedelta(minutes=20)
        token = create_access_token(user.username, user.id, expires_delta=token_expires)
        
        return {"token": token, "expires": token_expires}
    
    app.error(404, 'User not found, username or password is incorrect')

def get_user_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

def token_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    
if __name__ == '__main__':
    app.run(port=8001)

