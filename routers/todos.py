import models
from database import engine, get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from myapi import MyAPI
from .auth import get_current_user, get_user_exception


app = MyAPI()
router = app.api_router('todos')

models.Base.metadata.create_all(bind=engine)
        
class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description='The priority must be between 1 and 5')
    complete: bool

@router.post('/')
async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("user_id")
    
    db.add(todo_model)
    db.commit()
    return app.success(201)

@router.put('/{todo_id}')
async def update_todo(todo_id: int, todo: Todo, 
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("user_id"))\
        .first()
    
    if todo_model:
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.complete = todo.complete
        
        db.add(todo_model)
        db.commit()
        return app.success()
    app.error(404, 'Todo not found')
    
@router.delete('/{todo_id}')
async def delete_todo(todo_id: int, user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("user_id"))\
        .first()
    if todo_model:
        db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
        db.commit()
        return app.success(201)
    app.error(404, 'Todo not found')
    
    

@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()

@router.get('/user')
async def read_all_by_user(user:dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('user_id')).all()


@router.get('/{todo_id}')
async def read_todo(todo_id: int, user:dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("user_id"))\
        .first()
    if todo_model:
        return todo_model
    app.error(404, 'Todo not found in database')

if __name__ == '__main__':
    app.run()