from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベース接続設定
DATABASE_URL = "mysql+pymysql://username:password@hostname/dbname"  # 必要に応じて変更
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# ベースクラス
Base = declarative_base()

# データベース初期化関数
def init_db():
    Base.metadata.create_all(bind=engine)
