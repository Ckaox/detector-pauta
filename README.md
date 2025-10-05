# Ads Checker API

API web service para verificar anuncios de Google Ads y Meta/Facebook Ads por dominio.

## Características

- ✅ **Detección SIN APIs** - Análisis de tracking, scraping de bibliotecas públicas
- ✅ Consulta de anuncios de Google Ads por dominio
- ✅ Consulta de anuncios de Meta/Facebook Ads por dominio
- ✅ Consulta combinada de ambas plataformas
- ✅ **Análisis en lote** para bases de datos grandes
- ✅ **Sistema de scoring** y priorización
- ✅ API REST con documentación automática
- ✅ Respuestas estructuradas en JSON
- ✅ Manejo de errores robusto

## Estructura del Proyecto

```
ads-checker/
├── app/
│   ├── models/           # Modelos de datos (Pydantic)
│   ├── services/         # Servicios de negocio
│   ├── routers/          # Endpoints de la API
│   └── main.py           # Aplicación principal
├── requirements.txt      # Dependencias
├── .env.example         # Variables de entorno de ejemplo
└── README.md            # Esta documentación
```

## Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd ads-checker
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
# o
source venv/bin/activate  # En Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
copy .env.example .env
```

Edita el archivo `.env` con tus credenciales:
```env
GOOGLE_ADS_API_KEY=tu_clave_de_google_ads
META_ADS_ACCESS_TOKEN=tu_token_de_meta
META_ADS_APP_ID=tu_app_id_de_meta
META_ADS_APP_SECRET=tu_app_secret_de_meta
HOST=127.0.0.1
PORT=8000
DEBUG=True
```

## Ejecución

### Desarrollo
```bash
python run.py
```

### Producción con Gunicorn
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Deployment
- **Render**: Ver `DEPLOYMENT_GUIDE.md`
- **DigitalOcean**: Ver `DEPLOYMENT_GUIDE.md`
- **Vercel**: `vercel --prod`

## Uso de la API

### Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints Principales

#### 🆕 Detección SIN APIs (Recomendado para bases grandes)

##### 1. Análisis completo sin APIs
```http
GET /api/v1/no-api/analyze/{domain}
```

Ejemplo:
```bash
curl "http://localhost:8000/api/v1/no-api/analyze/nike.com"
```

Respuesta:
```json
{
  "domain": "nike.com",
  "likely_has_ads": true,
  "probability_score": 85.5,
  "confidence_level": "Muy Alta",
  "recommendation": "🟢 ALTA PRIORIDAD - Muy probable que tenga anuncios activos. Usar APIs para obtener detalles.",
  "next_steps": [
    "Usar Google Ads API para obtener detalles de anuncios",
    "Usar Meta Marketing API para información de Facebook/Instagram ads"
  ]
}
```

##### 2. Análisis en lote (perfecto para bases grandes)
```http
POST /api/v1/no-api/batch-analyze
```

Ejemplo:
```bash
curl -X POST "http://localhost:8000/api/v1/no-api/batch-analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "domains": ["nike.com", "adidas.com", "rockler.com"],
       "max_concurrent": 5
     }'
```

##### 3. Solo análisis de tracking del sitio web
```http
GET /api/v1/no-api/tracking/{domain}
```

#### 🔗 Endpoints con APIs (para detalles específicos)

##### 1. Consultar anuncios de un dominio
```http
GET /api/v1/ads/domain/{domain}?country_code=anywhere
```

Ejemplo:
```bash
curl "http://localhost:8000/api/v1/ads/domain/nike.com"
```

Respuesta:
```json
{
  "normalized_url": "nike.com",
  "google_ads": {
    "has_ads": false,
    "total_ad_count": 0,
    "continuation_token": null,
    "country_code": "anywhere",
    "message": "❌ No Ads found"
  },
  "meta_ads": {
    "has_ads": true,
    "number_of_ads": 78,
    "active_status": "active",
    "page_id": "15087023444",
    "message": "✅ 78 total ads found"
  }
}
```

#### 2. Consultar múltiples dominios
```http
POST /api/v1/ads/domains
```

Ejemplo:
```bash
curl -X POST "http://localhost:8000/api/v1/ads/domains" \
     -H "Content-Type: application/json" \
     -d '["nike.com", "adidas.com", "rockler.com"]'
```

#### 3. Solo Google Ads
```http
GET /api/v1/ads/domain/{domain}/google
```

#### 4. Solo Meta/Facebook Ads
```http
GET /api/v1/ads/domain/{domain}/meta
```

#### 5. Health Check
```http
GET /api/v1/ads/health
```

## Estructura de Respuesta

### Google Ads
```json
{
  "has_ads": true,
  "total_ad_count": 2000,
  "continuation_token": "CgoAP7zm/lmV8x3/EhBlGH2LHMfhFpMifkcAAAAAGgn8+Iqh+Bz9GaQ=",
  "country_code": "anywhere",
  "message": "✅ 2000 total ads found"
}
```

### Meta/Facebook Ads
```json
{
  "has_ads": true,
  "number_of_ads": 78,
  "active_status": "active",
  "page_id": "15087023444",
  "message": "✅ 78 total ads found"
}
```

## Integración con APIs Reales

### Google Ads API
Para integrar con la API real de Google Ads:

1. Obtén credenciales de Google Ads API
2. Configura `GOOGLE_ADS_API_KEY` en `.env`
3. Modifica `google_ads_service.py` para usar `search_ads_by_domain_real()`

### Meta Marketing API
Para integrar con la API real de Meta:

1. Crea una app en Facebook Developers
2. Obtén access token con permisos de ads_read
3. Configura las variables de Meta en `.env`
4. Modifica `meta_ads_service.py` para usar `search_ads_by_domain_real()`

## Desarrollo

### Estructura del Código

- **models/**: Definiciones de datos con Pydantic
- **services/**: Lógica de negocio y conexiones a APIs externas
- **routers/**: Definición de endpoints REST
- **main.py**: Configuración de FastAPI y aplicación principal

### Agregar Nuevas Funcionalidades

1. Agregar modelos en `models/`
2. Implementar lógica en `services/`
3. Crear endpoints en `routers/`
4. Actualizar documentación

## Testing

```bash
# Instalar dependencias de testing
pip install pytest httpx

# Ejecutar tests
pytest
```

## Licencia

MIT License

## Contribución

1. Fork el proyecto
2. Crea una branch para tu feature
3. Commit tus cambios
4. Push a la branch
5. Abre un Pull Request