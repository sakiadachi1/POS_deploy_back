from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from connect import get_db_connection, SessionLocal
from models import Product
from datetime import datetime
from zoneinfo import ZoneInfo
import pymysql
from fastapi.middleware.cors import CORSMiddleware
import os
import psutil

app = FastAPI()

# CORS 設定
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],# 開発時のみ "*" を使用、プロダクションでは特定のオリジンに制限する
    allow_credentials=True,
    allow_methods=["*"], # POSTメソッドを含むすべてのメソッドを許可
    allow_headers=["*"],
)

# 🔹 商品カートアイテムモデル (CartItem) を上に移動
class CartItem(BaseModel):
    code: str
    name: str
    price: int
    quantity: int = 1 # 仕様にはないが、仮で残す（必要なら削除）

# ✅ Pydantic モデル 購入リクエストモデル
class PurchaseRequest(BaseModel):
    emp_cd: str
    store_cd: Optional[str] = "30"  # 明示的にデフォルト値を設定
    pos_no: Optional[str] = "90"
    items: List[CartItem] = []  # カートのリスト

# # DB セッションの取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # 商品情報取得エンドポイント
@app.get("/product/{code}")
def get_product(code: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.code == code).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    return {"product": {"code": product.code, "name": product.name, "price": product.price}}


@app.post("/purchase")
def handle_purchase(request: PurchaseRequest,):
    if not request.items:
        raise HTTPException(status_code=400, detail="カートが空です")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 🔹 日本時間の現在日時を取得
        now = datetime.now(ZoneInfo("Asia/Tokyo"))

        # 🔹 取引テーブルにデータを挿入（TRD_IDは AUTO_INCREMENT）
        total_price = sum(item.price * item.quantity for item in request.items)
        cursor.execute(
            """
            INSERT INTO transactions_adachi (DATETIME, EMP_CD, STORE_CD, POS_NO, TOTAL_AMT) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (now, request.emp_cd, request.store_cd, request.pos_no, total_price)
        )

        # 🔹 取引IDの取得
        trd_id = cursor.lastrowid
        if trd_id is None:
            raise HTTPException(status_code=500, detail="取引IDの取得に失敗しました")

        # 🔹 取引詳細の挿入をバッチ処理で行わず、少しずつ挿入（transaction_details_adachiにデータを挿入）
        for item in request.items:
            cursor.execute("SELECT PRD_ID FROM m_product_adachi WHERE code = %s", (item.code,))
            product_data = cursor.fetchone()
            if not product_data:
                raise HTTPException(status_code=400, detail=f"商品コード {item.code} が見つかりません")
            
            prd_id = product_data[0]  # ✅ `fetchone()` のデータアクセス修正

            cursor.execute(
                """
                INSERT INTO transaction_details_adachi (TRD_ID, PRD_ID, PRD_CODE, PRD_NAME, PRD_PRICE) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (trd_id, prd_id, item.code, item.name, item.price)
            )
            # 途中でコミットすることで、メモリの消費を抑える
            conn.commit()

        # 最後にまとめてコミットする
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

    return {"trd_id": trd_id, "total_amt": total_price}


# # ✅ 購入処理
# @app.post("/purchase")
# def handle_purchase(request: PurchaseRequest,):
#     if not request.items:
#         raise HTTPException(status_code=400, detail="カートが空です")

#     try:
#         # conn = get_db_connection()
#         # cursor = conn.cursor()

#         # 🔹 日本時間の現在日時を取得
#         now = datetime.now(ZoneInfo("Asia/Tokyo"))

#         # 🔹 トランザクションテーブルへのデータ挿入（TRD_IDは AUTO_INCREMENT）
#         total_price = sum(item.price * item.quantity for item in request.items)
#         cursor.execute(
#             """
#             INSERT INTO transactions_adachi (DATETIME, EMP_CD, STORE_CD, POS_NO, TOTAL_AMT) VALUES (%s, %s, %s, %s, %s)
#             """,
#             (now, request.emp_cd, request.store_cd, request.pos_no, total_price)
#         )

#         # 🔹 取引IDの取得
#         trd_id = cursor.lastrowid
#         if trd_id is None:
#             raise HTTPException(status_code=500, detail="取引IDの取得に失敗しました")

#         # 🔹 取引詳細の挿入
#         for item in request.items:
#             cursor.execute("SELECT PRD_ID FROM m_product_adachi WHERE code = %s", (item.code,))
#             product_data = cursor.fetchone()
#             if not product_data:
#                 raise HTTPException(status_code=400, detail=f"商品コード {item.code} が見つかりません")
            
#             prd_id = product_data[0] # ✅ `fetchone()` のデータアクセス修正

#             # ✅ `transaction_details_adachi` に QUANTITY はないので削除
#             cursor.execute(
#                 """
#                 INSERT INTO transaction_details_adachi (TRD_ID, PRD_ID, PRD_CODE, PRD_NAME, PRD_PRICE) 
#                 VALUES (%s, %s, %s, %s, %s)
#                 """,
#                 (trd_id, prd_id, item.code, item.name, item.price)
#             )

#         conn.commit()
    
#     except pymysql.MySQLError as e:
#         conn.rollback()
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
#     except Exception as e:
#         conn.rollback()
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
#     finally:
#         cursor.close()
#         conn.close()

#     return {"trd_id": trd_id, "total_amt": total_price}
