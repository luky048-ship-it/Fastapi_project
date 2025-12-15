import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Настройка БД
if not os.path.exists("./data"):
    os.makedirs("./data")

DATABASE_URL = "sqlite:///./data/todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель задачи
class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine) # Автосоздание таблиц

# Схемы pydantic
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoResponse(TodoCreate):
    id: int
    completed: bool
    class Config:
        from_attributes = True

# API
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items", response_model=TodoResponse)
def create_item(item: TodoCreate, db: Session = Depends(get_db)):
    db_item = TodoItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items/{item_id}", response_model=TodoResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/items", response_model=List[TodoResponse])
def read_items(db: Session = Depends(get_db)):
    return db.query(TodoItem).all()

@app.put("/items/{item_id}", response_model=TodoResponse)
def update_item(item_id: int, updates_item: TodoCreate, db: Session = Depends(get_db)):
    db_item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in updates_item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}
