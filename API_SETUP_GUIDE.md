# 🔑 Guía para Obtener APIs de Google Ads y Meta

## 📊 Google Ads API

### Paso 1: Configuración inicial
1. **Crear cuenta de Google Ads** (si no tienes una):
   - Ve a [ads.google.com](https://ads.google.com)
   - Crea una cuenta (puedes pausar las campañas inmediatamente)

2. **Habilitar Google Ads API**:
   - Ve a [Google Cloud Console](https://console.cloud.google.com)
   - Crea un nuevo proyecto o selecciona uno existente
   - Busca "Google Ads API" y habilítala

### Paso 2: Credenciales
1. **Crear credenciales OAuth 2.0**:
   ```
   Google Cloud Console → APIs y servicios → Credenciales → Crear credenciales → ID de cliente OAuth 2.0
   ```
   
   **Configuración para desarrollo y producción:**
   - **Nombre**: `Ads Checker API Client`
   - **Tipo**: `Aplicación web`
   - **Orígenes JavaScript autorizados**:
     ```
     http://localhost:8000
     https://tu-app-name.onrender.com
     https://tu-dominio.com
     ```
   - **URIs de redireccionamiento autorizados**:
     ```
     http://localhost:8000/auth/callback
     https://tu-app-name.onrender.com/auth/callback
     https://tu-dominio.com/auth/callback
     urn:ietf:wg:oauth:2.0:oob
     ```

2. **Obtener Developer Token**:
   - Ve a [Google Ads](https://ads.google.com)
   - Tools & Settings → Setup → API Center
   - Solicita un Developer Token (puede tomar 24-48 horas)

### Paso 3: Configuración
```python
# Ejemplo de configuración
GOOGLE_ADS_DEVELOPER_TOKEN = "tu_developer_token"
GOOGLE_ADS_CLIENT_ID = "tu_client_id.apps.googleusercontent.com"
GOOGLE_ADS_CLIENT_SECRET = "tu_client_secret"
GOOGLE_ADS_REFRESH_TOKEN = "tu_refresh_token"
```

### Límites de Google Ads API:
- **Gratis**: 10,000 operaciones/día
- **Costo**: $2 por cada 1,000 operaciones adicionales
- **Rate Limit**: Varía según el nivel de acceso

---

## 📘 Meta Marketing API (Facebook/Instagram)

### Paso 1: Crear App de Facebook
1. **Facebook for Developers**:
   - Ve a [developers.facebook.com](https://developers.facebook.com)
   - Crear App → Tipo: "Empresa"

2. **Agregar Meta Marketing API**:
   - En tu app, agrega el producto "Marketing API"

### Paso 2: Permisos y tokens
1. **Permisos necesarios**:
   - `ads_read` - Para leer información de anuncios
   - `ads_management` - Para gestión completa
   - `business_management` - Para acceso a Business Manager

2. **Obtener Access Token**:
   - Herramientas → Graph API Explorer
   - Generar token con los permisos necesarios
   - **Importante**: Convertir a token de larga duración

### Paso 3: Business Verification
Para acceso completo necesitas:
- Verificación de negocio en Business Manager
- Revisar y aprobar la app (puede tomar días/semanas)

### Paso 4: Configuración
```python
# Ejemplo de configuración
META_APP_ID = "tu_app_id"
META_APP_SECRET = "tu_app_secret"
META_ACCESS_TOKEN = "tu_access_token_larga_duracion"
META_BUSINESS_ID = "tu_business_id"
```

### Límites de Meta Marketing API:
- **Rate Limits**: 200 llamadas/hora por defecto
- **Costo**: Gratis para consultas básicas
- **Restricciones**: Datos limitados sin verificación de negocio

---

## 🚀 Configuración para Deployment

### Render.com (Testing/Staging):
1. **URIs de OAuth para Render**:
   ```
   https://tu-app-name.onrender.com/auth/callback
   ```
   
2. **Variables de entorno en Render**:
   - Ir a Dashboard → tu-app → Environment
   - Agregar todas las variables del `.env`

3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### DigitalOcean (Producción):
1. **URIs de OAuth para DO**:
   ```
   https://tu-dominio.com/auth/callback
   https://api.tu-dominio.com/auth/callback
   ```

2. **App Platform o Droplet**:
   - **App Platform**: Similar a Render
   - **Droplet**: Configurar nginx + gunicorn

3. **Variables de entorno**:
   ```bash
   export GOOGLE_ADS_CLIENT_ID="tu_client_id"
   export META_ACCESS_TOKEN="tu_token"
   ```

### Configuración Rápida para Testing:

### Para Google Ads (Testing):
1. Usa tu cuenta personal de Google Ads
2. Solicita Developer Token para testing
3. Usa OAuth playground para obtener tokens

### Para Meta (Testing):
1. Crea app de desarrollo
2. Usa tu propia cuenta de Facebook Business
3. Genera tokens con Graph API Explorer

---

## 📋 Checklist de Configuración

### Google Ads ✅
- [ ] Cuenta de Google Ads activa
- [ ] Proyecto en Google Cloud Console
- [ ] Google Ads API habilitada
- [ ] Credenciales OAuth 2.0 creadas
- [ ] Developer Token solicitado y aprobado
- [ ] Refresh Token generado

### Meta Marketing ✅
- [ ] App en Facebook for Developers
- [ ] Marketing API agregada a la app
- [ ] Permisos configurados (`ads_read`)
- [ ] Access Token de larga duración generado
- [ ] Business Manager configurado (opcional para testing)

---

## 🔧 Testing Sin APIs Completas

Mientras obtienes las APIs, puedes usar:

1. **Método Sin APIs** (ya implementado):
   ```bash
   GET /api/v1/no-api/analyze/{domain}
   ```

2. **Simulación con datos reales**:
   - Usar bibliotecas públicas
   - Análisis de tracking en sitios web
   - Scraping de información pública

3. **APIs de prueba**:
   - Google Ads: Sandbox environment
   - Meta: Modo desarrollador con datos limitados

---

## ⚡ Alternativas Rápidas

### 1. Servicios de terceros:
- **AdBeat**: API para inteligencia competitiva
- **SEMrush API**: Información de anuncios
- **SimilarWeb API**: Datos de tráfico y ads

### 2. Scraping legal:
- Facebook Ad Library (público)
- Google Ads Transparency Center
- Análisis de código fuente de sitios web

---

## 💡 Recomendación para Bases Grandes

1. **Fase 1**: Usar métodos sin API para filtrar
2. **Fase 2**: APIs solo para dominios con alta probabilidad
3. **Ahorro estimado**: 60-80% menos llamadas API

Ejemplo:
```
1000 dominios → Filtro sin API → 200 candidatos → Solo 200 llamadas API
Ahorro: 800 llamadas API 💰
```