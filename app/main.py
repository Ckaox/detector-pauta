from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from .routers import ads_router, no_api_router, ultra_router
from .routers.unified_without_apis import router as without_apis_router
from .routers.unified_with_apis import router as with_apis_router
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
app.include_router(without_apis_router)  # 🚀 NUEVO: Endpoint principal sin APIs
app.include_router(with_apis_router)     # 🚀 NUEVO: Endpoint principal con APIs

# Routers legacy (mantener por compatibilidad)
app.include_router(ads_router)
app.include_router(no_api_router)
app.include_router(ultra_router)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API unificada"""
    return {
        "message": "🚀 Ads Checker API - Sistema Unificado de Detección",
        "version": "3.0.0",
        "docs": "/docs",
        "endpoints_principales": {
            "sin_apis": {
                "url": "/api/v1/without-apis/",
                "descripcion": "Detección sin APIs pagadas (85-95% precisión)",
                "metodos": ["ultra", "basic", "facebook-only"],
                "costo": "Gratuito",
                "uso_recomendado": "Pre-filtrado de bases de datos grandes"
            },
            "con_apis": {
                "url": "/api/v1/with-apis/",
                "descripcion": "Detección con APIs oficiales (99% precisión)",
                "apis": ["Google Ads API", "Meta Marketing API"],
                "costo": "Pagado por llamada",
                "uso_recomendado": "Dominios ya pre-filtrados"
            }
        },
        "flujo_recomendado": [
            "1. Filtrar dominios con /without-apis (ahorro 80-90%)",
            "2. Analizar prioritarios con /with-apis (datos exactos)",
            "3. Tomar decisiones basadas en datos precisos"
        ],
        "nuevas_funcionalidades": [
            "📘 Transparencia avanzada de Facebook",
            "🔬 Scraping de 'anuncios en circulación'",
            "📊 Endpoints unificados y simplificados",
            "💰 Calculadora de costos integrada"
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