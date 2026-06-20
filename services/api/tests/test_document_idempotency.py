"""Document generation idempotency tests."""

from types import SimpleNamespace

from app.public_api.documents import unique_report_documents
from app.services.document_service import should_schedule_generation


def _job(status: str) -> SimpleNamespace:
    return SimpleNamespace(status=status)


def _doc(file_path: str, fmt: str = "md") -> SimpleNamespace:
    return SimpleNamespace(file_path=file_path, format=fmt)


def test_document_generation_only_schedules_new_or_failed_jobs():
    assert should_schedule_generation(_job("queued"), created=True)
    assert should_schedule_generation(_job("failed"), created=False)

    assert not should_schedule_generation(_job("queued"), created=False)
    assert not should_schedule_generation(_job("generating"), created=False)
    assert not should_schedule_generation(_job("ready"), created=False)


def test_report_status_deduplicates_artifacts_by_filename():
    docs = [
        _doc("reports/aia_1/rep_1/01_risk_classification_memo.md"),
        _doc("reports/aia_1/rep_1/evidence_pack.zip", "zip"),
        _doc("reports/aia_1/rep_1/01_risk_classification_memo.md"),
        _doc("reports/aia_1/rep_1/evidence_pack.zip", "zip"),
    ]

    unique_docs = unique_report_documents(docs)

    assert [doc.file_path.rsplit("/", 1)[-1] for doc in unique_docs] == [
        "01_risk_classification_memo.md",
        "evidence_pack.zip",
    ]
