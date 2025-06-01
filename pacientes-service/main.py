from fastapi import FastAPI
from routers import paciente

app = FastAPI()

app.include_router(paciente.router)