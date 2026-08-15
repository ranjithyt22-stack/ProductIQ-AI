"""
Database connection, session management, and table initializer for ProductIQ AI.
Compatible with SQLite (default zero-configuration local file) and PostgreSQL.
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Environment configurable database URI with local SQLite fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/productiq.db")

# SQLite-specific connect args
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for standalone repository operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initializes all database tables safely and adds missing columns automatically."""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    # Import models so Base metadata is fully populated before create_all
    import backend.database.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Auto-add new columns to existing SQLite tables if missing
    if DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            # Check product_specifications columns
            try:
                res = conn.exec_driver_sql("PRAGMA table_info(product_specifications)").fetchall()
                existing_cols = [r[1] for r in res]

                new_spec_cols = [
                    ("normalization_applied", "BOOLEAN DEFAULT 0"),
                    ("normalization_rule", "VARCHAR(128)"),
                    ("source_reliability", "VARCHAR(64) DEFAULT 'OFFICIAL_DATASHEET'"),
                    ("evidence_type", "VARCHAR(32) DEFAULT 'DIRECT'"),
                    ("match_status", "VARCHAR(32) DEFAULT 'VERIFIED'"),
                    ("confidence_level", "VARCHAR(32) DEFAULT 'HIGH'"),
                    ("review_required", "BOOLEAN DEFAULT 0"),
                    ("review_reason", "TEXT")
                ]
                for col_name, col_type in new_spec_cols:
                    if col_name not in existing_cols:
                        conn.exec_driver_sql(f"ALTER TABLE product_specifications ADD COLUMN {col_name} {col_type}")

                # Check evidence_records columns
                ev_res = conn.exec_driver_sql("PRAGMA table_info(evidence_records)").fetchall()
                existing_ev_cols = [r[1] for r in ev_res]

                new_ev_cols = [
                    ("product_id", "VARCHAR(64)"),
                    ("version_id", "VARCHAR(64)"),
                    ("attribute_name", "VARCHAR(255)"),
                    ("raw_value", "VARCHAR(512)"),
                    ("normalized_value", "VARCHAR(512)"),
                    ("source_location", "VARCHAR(255)"),
                    ("evidence_type", "VARCHAR(32) DEFAULT 'DIRECT'"),
                    ("match_status", "VARCHAR(32) DEFAULT 'VERIFIED'")
                ]
                for col_name, col_type in new_ev_cols:
                    if col_name not in existing_ev_cols:
                        conn.exec_driver_sql(f"ALTER TABLE evidence_records ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except Exception:
                pass

