from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from .routers.unified_simple import router as unified_router
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

# Incluir router unificado simple
app.include_router(unified_router)


@app.get("/")
async def root():
    """API ultra-simplificada con solo 2 endpoints"""
    return {
        "message": "🚀 Ads Checker API - Ultra Simplificada",
        "version": "4.0.0",
        "docs": "/docs",
        "endpoints": {
            "sin_apis": {
                "url": "POST /api/v1/without-apis",
                "input": "dominio o URL de Facebook",
                "descripcion": "Análisis completo GRATIS (85-95% precisión)",
                "incluye": "Transparencia Facebook automática",
                "costo": "Gratuito"
            },
            "con_apis": {
                "url": "POST /api/v1/with-apis", 
                "input": "dominio o URL de Facebook",
                "descripcion": "APIs oficiales + transparencia Facebook",
                "incluye": "Datos exactos Google & Meta",
                "costo": "Pagado"
            }
        },
        "input_examples": {
            "domain": "nike.com",
            "facebook_url": "https://facebook.com/nike",
            "json": {"domain": "nike.com", "facebook_url": "https://facebook.com/nike"}
        },
        "nueva_funcionalidad": [
            "📘 Transparencia Facebook automática",
            "� Input con URL de Facebook directa",
            "📊 JSON response unificado",
            "⚡ Solo 2 endpoints simples"
        ]
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