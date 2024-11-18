from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DB_HOST = "localhost"
DB_NAME = "eBoi"
DB_USER = "postgres"
DB_PASS = "root"
DB_PORT = "5432"

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
