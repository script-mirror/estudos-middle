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
    git_username: str
    git_token: str
    
    # Prospec API Configuration
    api_prospec_base_url: str = "https://api.prospec.app"
    api_prospec_username: str
    api_prospec_password: str
    path_arquivos: str = "/projetos/arquivos"
    path_projetos: str = "/projetos"
    
    # Prospec Server Configuration
    server_deflate_prospec: str = ""
    path_prevs_prospec: str = ""
    path_results_prospec: str = ""
    path_prevs_interno: str = ""

    # Email Configuration
    email_host: str
    email_port: int = 587
    email_user: str
    email_pass: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
