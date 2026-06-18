"""Background document generation."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.services.document_service import run_generation_sync


def run_generate_document(report_id: str) -> None:
    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        run_generation_sync(session, report_id)
