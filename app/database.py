import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Na Vercel (serverless), a gravacao de arquivos so e permitida em /tmp
if os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/barbearia.db"
else:
    DATABASE_URL = "sqlite:///./barbearia.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
