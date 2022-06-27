from myapi import MyAPI

router = MyAPI().api_router()

@router.get('/')
async def get_company_name():
    return {"company_name": "Example Company, LLC"}

@router.get('/employees')
async def employees():
    return 162