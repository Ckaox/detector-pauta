from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from .routers import ads_router, no_api_router, ultra_router
from .models import ErrorResponse
from .config import settings

# Cargar variables de entorno
load_dotenv()

# Crear instancia de FastAPI
app = FastAPI(
    title="Ads Checker API",
    description="API para verificar anuncios de Google Ads y Meta/Facebook Ads por dominio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(ads_router)
app.include_router(no_api_router)
app.include_router(ultra_router)


@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "Ads Checker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/ads/health"
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejador personalizado para errores 404"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Not Found",
            message="El endpoint solicitado no existe",
            status_code=404
        ).dict()
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Manejador personalizado para errores 500"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="Error interno del servidor",
            status_code=500
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )