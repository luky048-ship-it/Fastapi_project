import os
import string
import random
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

""" Настройка базы данных (SQLite) """
# Создаем папку data, если ее нет
if not os.path.exists("./data"):
    os.makedirs("./data")

DATABASE_URL = 'sqlite:///./data/shorturl.db' # Путь к БД

# Создаем движок (engine) для подключение
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Описание модели данных (таблица БД)
class URLItem(Base):
    __tablename__ = "urls"

    short_id = Column(String, primary_key=True, index=True) # короткий ключ

    full_url = Column(String, index=True) # полная ссылка



Base.metadata.create_all(bind=engine) # автоматическое создание таблицы при запуске

""" pydantic схемы """

class URLCreate(BaseModel):
    url: str
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Генератор случайного короткого ID
def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))



# Post /shorten: Создание короткой ссылки
@app.post("/shorten")
def shorten_url(item: URLCreate, db: Session = Depends(get_db)):
    short_id = generate_short_id() # Генерируем уникальный ID

    # Проверка коллизий
    while db.query(URLItem).filter(URLItem.short_id == short_id).first():
        short_id = generate_short_id()

# Создаем запись в БД
    new_url = URLItem(short_id=short_id, full_url=item.url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {"short_url": short_id, "full_url": item.url}



# Get /{short_id}: Перенаправление
@app.get("/{short_id}")
def redirect_to_full(short_id: str, db: Session = Depends(get_db)):
    db_url = db.query(URLItem).filter(URLItem.short_id == short_id).first()

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url=db_url.full_url)



# GET /status/{short_id}: Информация о ссылке
@app.get("/stats/{short_id}")
def get_stats(short_id: str, db: Session = Depends(get_db)):
    db_url = db.query(URLItem).filter(URLItem.short_id == short_id).first()

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"short_id": db_url.short_id, "full_url": db_url.full_url}




