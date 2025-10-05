#!/usr/bin/env python3
"""
Script de inicio para el servidor de desarrollo
"""

import os
import sys
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Iniciando Ads Checker API en {settings.BASE_URL}")
    print(f"📚 Documentación disponible en {settings.BASE_URL}/docs")
    print(f"🔧 Modo debug: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )