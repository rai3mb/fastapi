from fastapi import FastAPI, HTTPException, APIRouter, Depends
import uvicorn, os, __main__

class MyAPI(FastAPI):
    def __init__(self):
        super(MyAPI, self).__init__(title='Minha API',
                                    version='0.1.0',
                                    description='Descrição mais completa da API',
                                    contact={
                                        'name': 'Raimundo Portela',
                                        'url': 'http://portelanet.com',
                                        'email': 'rai3mb@gmail.com',
                                    })
        
    def run(self, port=8000):
        #app = self
        name = os.path.basename(__main__.__file__).split('.')[0]
        uvicorn.run("%s:app" % name, host="0.0.0.0", port=port, reload=True, server_header=False)
        
    def error(self, status: int = 404, message: str = 'Not Found'):
        raise HTTPException(status_code=status, detail=message)
    
    def success(self, status: int = 200, message: str = 'Successful'):
        return {
            'status': status,
            'transaction': message
        }
        
    def api_router(self, prefix=None):
        if prefix is None:
            return APIRouter()
        return APIRouter(
            prefix=f'/{prefix}' ,
            tags=[prefix],
            responses={401: {'user': 'Not authorized'}}
        )
        
    