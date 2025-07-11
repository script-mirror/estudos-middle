import locale
from app.core.config import settings
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from app.core.dependencies import cognito
from app.modules.ccee.controller import router as ccee_router


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

auth_scheme = HTTPBearer()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url
)

app.include_router(
    ccee_router,
    prefix=settings.app_prefix,
    dependencies=[
        # Depends(auth_scheme),
        # Depends(cognito.auth_required),
    ]
)
