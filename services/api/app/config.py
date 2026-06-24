from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://aia:aia@localhost:5432/aia_navigator"
    database_url_sync: str = "postgresql://aia:aia@localhost:5432/aia_navigator"
    redis_url: str = "redis://localhost:6379/0"

    api_cors_origins: str = "http://localhost:3000"
    secret_key: str = "dev-secret-change-me"

    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket: str = "aia-documents"
    s3_region: str = "us-east-1"

    clerk_secret_key: str | None = None
    clerk_jwks_url: str | None = None

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_evidence_pack: str | None = None

    dodo_payments_api_key: str | None = None
    dodo_payments_webhook_key: str | None = None
    dodo_payments_environment: str = "live_mode"
    dodo_product_evidence_pack: str | None = None

    admin_api_key: str = "dev-admin-key"
    web_base_url: str = "http://localhost:3000"
    resend_api_key: str | None = None
    transactional_from_email: str = "AI Act Navigator <noreply@originalnexus.com>"
    download_token_ttl_seconds: int = 3600
    dev_mode: bool = True

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


settings = Settings()
