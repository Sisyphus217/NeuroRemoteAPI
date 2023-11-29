# main.py
from app.task import Task
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# Инициализация FastAPI приложения
app = FastAPI()

# Подключение к MongoDB
client = AsyncIOMotorClient("127.0.0.1:27017")
db = client["tasks"]
collection = db["tasks"]

# Модель данных для задачи
class Task(BaseModel):
    id: str
    description: str
    network_id: str

# Роут для создания задачи
@app.post("/create_task")
async def create_task(task: Task):
    try:
        # Проверяем, есть ли уже задача с таким ID
        existing_task = await collection.find_one({"id": task.id})
        if existing_task:
            # Если задача существует, возвращаем ошибку
            raise HTTPException(status_code=400, detail="Task with this ID already exists")

        # Добавляем задачу в MongoDB
        created_task = await collection.insert_one(task.dict())

        # Создаем папку для задачи внутри папки neuro
        task_folder_path = f"neuro/{task.network_id}/{str(created_task.inserted_id)}"
        os.makedirs(task_folder_path, exist_ok=True)

        # Возвращаем успешный ответ
        return {"message": "Task created successfully"}
    except Exception as e:
        # Если произошла ошибка, возвращаем ошибку сервера
        raise HTTPException(status_code=500, detail=str(e))

# Функция для извлечения задачи по id
async def get_task(task_id: str):
    task = await collection.find_one({"_id": ObjectId(task_id)})
    return task

# Роут для получения задачи по id
@app.get("/get_task/{task_id}", response_model=Task)
async def read_task(task_id: str):
    task = await get_task(task_id)
    if task:
        return task
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# Роут для удаления задачи по id
@app.delete("/delete_task/{task_id}", response_model=Task)
async def delete_task(task_id: str):
    task = await get_task(task_id)
    if task:
        # Удаляем задачу
        await collection.delete_one({"_id": ObjectId(task_id)})
        return task
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# Роут для обновления задачи по id
@app.put("/update_task/{task_id}", response_model=Task)
async def update_task(task_id: str, updated_task: dict):
    existing_task = await get_task(task_id)
    if existing_task:
        # Обновляем поле только поле description!!!
        await collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"description": updated_task["description"]}}
        )
        # Получаем обновленную задачу
        updated_task = await get_task(task_id)
        return updated_task
    else:
        raise HTTPException(status_code=404, detail="Task not found")       

@app.get("/")
def read_root():
    return {"Hello": "World"}