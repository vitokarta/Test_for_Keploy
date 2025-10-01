import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 支援環境變數配置，默認使用 SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./students.db"
)

# 根據資料庫類型設定連接參數
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # MySQL 連接
    engine = create_engine(
        DATABASE_URL,
        echo=True  # 開發時顯示 SQL 查詢
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()