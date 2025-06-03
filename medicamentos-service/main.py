from fastapi import FastAPI
from routers import medicamento

app = FastAPI()

app.include_router(medicamento.router)