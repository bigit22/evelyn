from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ai_provider: str = "openrouter"
    ai_api_key: str = ""
    hh_client_id: str = ""
    hh_client_secret: str = ""
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
