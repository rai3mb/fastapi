from myapi import MyAPI, Depends
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, get_user_exception, verify_password, get_password_hash

app = MyAPI()
router =app.api_router('users')

models.Base.metadata.create_all(bind=engine)

class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str

@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router.get('/user/{user_id}')
async def user_by_path(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    app.error()
    
@router.get('/user/')
async def user_by_query(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    app.error()
    
@router.put('/user/password')
async def user_password_change(user_verification: UserVerification, user: dict = Depends(get_current_user),
                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    user_model = db.query(models.Users).filter(models.Users.id == user.get('user_id')).first()
    if user_model is not None:
        if user_verification.username == user_model.username and\
            verify_password(user_verification.password, user_model.hashed_password):
            
            user_model.hashed_password = get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return app.success()
    return app.error(416, 'Invalid user request')
    
@router.delete('/user')
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    user_model = db.query(models.Users).filter(models.Users.id == user.get('user_id')).first()
    
    if user_model is None:
        return 'Invalid user or request'
    
    db.query(models.Users).filter(models.Users.id == user.get('user_id')).delete()
    db.commit()
    
    return 'Deleted Successful'