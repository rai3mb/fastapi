import sys
import models
from database import engine

sys.path.append('/Users/raiportela/cursos/libs/')
sys.path.append('.')
from myapi import MyAPI, Depends
from routers import auth, todos, users
from company import companyapis, dependencies

app = MyAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(
    companyapis.router,
    prefix='/companyapis',
    tags=['companyapis'],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={418: {'description': 'Internal User Only'}}
)

if __name__ == '__main__':
    app.run()