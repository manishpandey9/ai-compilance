from app import storage


class _FakeS3Client:
    def __init__(self) -> None:
        self.put_calls = []
        self.objects = {"reports/sample.md": b"sample"}

    def put_object(self, **kwargs):
        self.put_calls.append(kwargs)

    def get_object(self, Bucket: str, Key: str):
        return {"Body": _FakeBody(self.objects[Key])}


class _FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class _FakeGcsClient:
    def __init__(self) -> None:
        self.bucket_instance = _FakeGcsBucket()

    def bucket(self, name: str):
        self.bucket_name = name
        return self.bucket_instance


class _FakeGcsBucket:
    def __init__(self) -> None:
        self.blob_instance = _FakeGcsBlob()

    def blob(self, name: str):
        self.blob_name = name
        return self.blob_instance


class _FakeGcsBlob:
    def __init__(self) -> None:
        self.uploaded = None
        self.download_data = b"gcs sample"

    def upload_from_string(self, data: bytes, content_type: str):
        if not isinstance(data, bytes):
            raise TypeError(f"{type(data).__name__} could not be converted to bytes")
        self.uploaded = (data, content_type)

    def download_as_bytes(self) -> bytes:
        return self.download_data


def test_storage_uses_s3_compatible_client_by_default(monkeypatch):
    fake = _FakeS3Client()
    monkeypatch.setattr(storage.settings, "s3_endpoint_url", "http://localhost:9000")
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")
    monkeypatch.setattr(storage, "get_s3_client", lambda: fake)

    key = storage.upload_bytes("reports/sample.md", b"hello", "text/markdown")
    data = storage.download_bytes("reports/sample.md")

    assert key == "reports/sample.md"
    assert fake.put_calls == [
        {
            "Bucket": "test-bucket",
            "Key": "reports/sample.md",
            "Body": b"hello",
            "ContentType": "text/markdown",
        }
    ]
    assert data == b"sample"


def test_storage_uses_gcs_when_endpoint_is_gcs(monkeypatch):
    fake = _FakeGcsClient()
    monkeypatch.setattr(storage.settings, "s3_endpoint_url", "gcs")
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")
    monkeypatch.setattr(storage, "get_gcs_client", lambda: fake)

    key = storage.upload_bytes("reports/sample.md", b"hello", "text/markdown")
    data = storage.download_bytes("reports/sample.md")

    assert key == "reports/sample.md"
    assert fake.bucket_name == "test-bucket"
    assert fake.bucket_instance.blob_name == "reports/sample.md"
    assert fake.bucket_instance.blob_instance.uploaded == (b"hello", "text/markdown")
    assert data == b"gcs sample"


def test_gcs_upload_normalizes_bytearray_payloads(monkeypatch):
    fake = _FakeGcsClient()
    monkeypatch.setattr(storage.settings, "s3_endpoint_url", "gcs")
    monkeypatch.setattr(storage.settings, "s3_bucket", "test-bucket")
    monkeypatch.setattr(storage, "get_gcs_client", lambda: fake)

    storage.upload_bytes("reports/procurement.pdf", bytearray(b"%PDF"), "application/pdf")

    assert fake.bucket_instance.blob_instance.uploaded == (b"%PDF", "application/pdf")
