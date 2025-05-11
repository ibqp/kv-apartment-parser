import os

user = os.environ.get('PG_LOC_DB_USER')
pw = os.environ.get('PG_LOC_DB_PASS')
db = os.environ.get('PG_LOC_DB_NAME')
host = os.environ.get('PG_LOC_DB_HOST', 'localhost')
port = os.environ.get('PG_LOC_DB_PORT', '5432')

DATABASE_URL = f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{db}"
