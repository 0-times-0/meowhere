from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/meowhere_db"

    # ------------------------------------------------------------------
    # JWT
    # Do podpisywania tokenów używamy JWT_SECRET_KEY, a gdy go nie ma,
    # spadamy na SECRET_KEY. Wcześniej kod czytał atrybut, którego tu
    # nie było -> AttributeError przy każdym tokenie.
    # ------------------------------------------------------------------
    JWT_SECRET_KEY: SecretStr | None = None
    SECRET_KEY: SecretStr = SecretStr(
        "dev-only-secret-key-change-in-production-minimum-32-chars"
    )
    JWT_ALGORITHM: str = "HS256"
    ALGORITHM: str = "HS256"  # alias zgodnościowy
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    # Dane konta demo dla Straży Miejskiej (używane przez seeder).
    DEMO_MUNICIPAL_BADGE: str = "SM-101"
    DEMO_MUNICIPAL_PASSWORD: str = "StrazMiejska123!"
    DEMO_MUNICIPAL_NAME: str = "Patrol Eko Straży Miejskiej"
    DEMO_MUNICIPAL_UNIT: str = "Eko-Patrol Warszawa"
    DEMO_MUNICIPAL_EMAIL: str = "sm101@example.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def signing_key(self) -> str:
        """Klucz, którym realnie podpisujemy i weryfikujemy tokeny JWT."""

        key = self.JWT_SECRET_KEY or self.SECRET_KEY
        return key.get_secret_value()

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()