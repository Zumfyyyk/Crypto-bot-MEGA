import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Создаем базовый класс модели
class Base(DeclarativeBase):
    pass

# Инициализируем SQLAlchemy
db = SQLAlchemy(model_class=Base)