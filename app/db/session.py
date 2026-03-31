from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

database_url = settings.database_url
engine_kwargs = {"pool_pre_ping": True}

if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite:///:memory:"):
	db_path_raw = database_url.replace("sqlite:///", "", 1)
	db_path = Path(db_path_raw)
	if not db_path.is_absolute():
		project_root = Path(__file__).resolve().parents[2]
		db_path = (project_root / db_path).resolve()
	db_path.parent.mkdir(parents=True, exist_ok=True)
	database_url = f"sqlite:///{db_path}"

if database_url.startswith("sqlite"):
	engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
