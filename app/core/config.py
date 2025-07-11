from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Estudos Middle - API"
    version: str = "2.0.0"
    app_prefix: str = "/estudos-middle/api"
    docs_url: str = f"{app_prefix}/docs"
    redoc_url: str = f"{app_prefix}/redoc"
    openapi_url: str = f"{app_prefix}/openapi.json"
    cognito_url: str
    cognito_config: str
    aws_region: str
    cognito_userpool_id: str
    url_api_middle: str = "http://0.0.0.0:8000/api/v2"
    url_dados_abertos_ccee: str = "https://dadosabertos.ccee.org.br/dataset"
    url_api_ccee: str = (
        "https://dadosabertos.ccee.org.br/api/3/action/datastore_search"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
