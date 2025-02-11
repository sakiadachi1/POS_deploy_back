from models import Base  # models.pyで定義されたBaseをインポート
from connect import engine

# テーブル作成用関数
def create_all_tables():
    print("Creating tables >>>")
    Base.metadata.create_all(bind=engine)  # すべてのテーブルを作成

if __name__ == "__main__":
    create_all_tables()
    print("All tables are created successfully.")
