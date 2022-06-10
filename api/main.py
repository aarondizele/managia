from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from api.routers import (
    archives,
    auth
)

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = [
    'http://localhost:3000',
    'http://localhost:3001',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event("startup")
async def startup_event():
    load_dotenv()


app.include_router(archives.router, prefix='/api/v1')
app.include_router(auth.router, prefix='/api/v1')