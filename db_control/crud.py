from sqlalchemy.orm import sessionmaker
from connect import engine

# セッション構築
Session = sessionmaker(bind=engine)

# データ挿入 (単一レコード)
def insert_record(model, record):
    session = Session()
    try:
        with session.begin():
            session.add(record)
        print(f"Record added: {record}")
    except Exception as e:
        print(f"Error adding record: {e}")
        session.rollback()
    finally:
        session.close()

# データ取得 (全レコード)
def get_all_records(model):
    session = Session()
    try:
        with session.begin():
            results = session.query(model).all()
        return results
    except Exception as e:
        print(f"Error fetching records: {e}")
    finally:
        session.close()
