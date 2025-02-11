import os
import tempfile
import mysql.connector
import ssl
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote

# .env をロード
load_dotenv(dotenv_path=".env", override=True)

# 環境変数の取得
db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_host = os.getenv("MYSQL_HOST")
db_name = os.getenv("MYSQL_DATABASE")

# パスワードを URL エンコード（ `@` → `%40` ）
db_password_encoded = quote(db_password)

# SSL証明書の取得
SSL_CA_CERT = os.getenv("SSL_CA_CERT")
if not SSL_CA_CERT:
    raise ValueError("❌ SSL_CA_CERT が設定されていません！")

# SSL証明書の一時ファイル作成
def create_ssl_cert_tempfile():
    pem_content = SSL_CA_CERT.replace("\\n", "\n").replace("\\", "")
    temp_pem = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w")
    temp_pem.write(pem_content)
    temp_pem.close()
    return temp_pem.name

ssl_ca_path = create_ssl_cert_tempfile()

# MySQL への接続
engine = create_engine(
    f"mysql+pymysql://{db_user}:{db_password_encoded}@{db_host}/{db_name}?ssl_ca={ssl_ca_path}",
    pool_pre_ping=True
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MySQL に直接接続する関数
def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        ssl_ca=ssl_ca_path
    )

# 環境変数のチェック（デバッグ用）
print(f"✅ MySQL USER: {db_user}")
print(f"✅ MySQL HOST: {db_host}")
print(f"✅ MySQL DATABASE: {db_name}")
