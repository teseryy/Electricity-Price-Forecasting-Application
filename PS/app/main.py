from fastapi import FastAPI

from app.Depedencies import lifespan
from app.controller.ForecastController import router
from app.service.connection.KafkaService import kafka_router

app = FastAPI(lifespan=lifespan)

app.include_router(router)

app.include_router(kafka_router)