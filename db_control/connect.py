import os
import tempfile
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Azure MySQL の接続情報
DATABASE_URL = os.getenv("DATABASE_URL")
SSL_CA_CERT = os.getenv("SSL_CA_CERT")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

print(f"Using DATABASE_URL: {DATABASE_URL}")

try:
    print("=== Connecting to AzureDB ===")

    # SSL証明書の確認
    if not SSL_CA_CERT:
        raise ValueError("SSL_CA_CERT is not set in environment variables.")

    # 証明書の改行を修正
    SSL_CA_CERT = SSL_CA_CERT.replace("\\n", "\n").replace("\\", "")

    # 一時ファイル作成（SSL証明書を保存）
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".pem") as temp_pem:
        temp_pem.write(SSL_CA_CERT)
        temp_pem_path = temp_pem.name

    with open(temp_pem_path, "r") as temp_pem:
        print("===== Temporary certificate file content: =====")
        print(temp_pem_path)
        print(temp_pem.read())

    # Azure MySQL に接続
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "ssl": {
                "ca": temp_pem_path
            }
        }
    )

except Exception as e:
    print(f"Error during database connection setup: {e}")
    raise
