
from fastapi import FastAPI
import uvicorn
from api.routes.blog import router as blog_router
from api.routes.user import router as user_router
from auth.auth import router as auth_router
from middlewares.middleware import add_cors_middleware

app = FastAPI()

add_cors_middleware(app)



router = app.include_router(auth_router,tags=["auth"])
router = app.include_router(user_router,tags=["user"])
router = app.include_router(blog_router, tags=["blogs"])


@app.get('/')
async def home():
    return {"Welcome to Xpress!"}

@app.get('/plans')
async def plans():
    return {"Welcome to Xpress plans!"}




if __name__ == "__main__":
    port = int(8000)

    app_module = "main:app"
    uvicorn.run(app_module, host="0.0.0.0", port=port, reload=True)




