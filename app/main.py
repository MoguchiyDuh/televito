from fastapi import FastAPI
from .routes.user_route import router as user_route

app = FastAPI()

app.include_router(user_route, prefix="/users")


@app.get("/")
async def home():
    return {"message": "Welcome to the User Management API!"}
