from sqlalchemy.orm import sessionmaker
from connect import engine  # connect.pyで定義されたengineを使用
from mymodels import Products  # Productsテーブルのモデル

# セッションを構築
Session = sessionmaker(bind=engine)
session = Session()

# ダミーデータ
dummy_data = [
    {"code": "11111111111", "name": "ダミー商品A", "price": 100},
    {"code": "22222222222", "name": "ダミー商品B", "price": 200},
    {"code": "33333333333", "name": "ダミー商品C", "price": 300},
    {"code": "44444444444", "name": "ダミー商品D", "price": 400},
    {"code": "55555555555", "name": "ダミー商品E", "price": 500},
]

# データベースに挿入
try:
    for data in dummy_data:
        new_product = Products(code=data["code"], name=data["name"], price=data["price"])
        session.add(new_product)
    session.commit()
    print("ダミーデータが挿入されました。")
except Exception as e:
    print(f"データ挿入中にエラーが発生しました: {e}")
    session.rollback()
finally:
    session.close()
