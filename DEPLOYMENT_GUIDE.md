# 🚀 Deployment Guide

## Render.com (Recomendado para testing)

### Paso 1: Preparar el proyecto
1. **Subir a GitHub** (si no lo has hecho):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/ads-checker.git
   git push -u origin main
   ```

### Paso 2: Configurar Render
1. **Crear cuenta en [render.com](https://render.com)**
2. **Conectar repositorio de GitHub**
3. **Crear Web Service**:
   - **Name**: `ads-checker-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Paso 3: Variables de entorno en Render
```env
GOOGLE_ADS_API_KEY=tu_api_key
GOOGLE_ADS_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=tu_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=tu_developer_token
GOOGLE_ADS_REFRESH_TOKEN=tu_refresh_token

META_ADS_ACCESS_TOKEN=tu_access_token
META_ADS_APP_ID=tu_app_id
META_ADS_APP_SECRET=tu_app_secret

HOST=0.0.0.0
PORT=10000
DEBUG=False
```

### Paso 4: Actualizar credenciales OAuth
En Google Cloud Console, agregar:
```
https://tu-app-name.onrender.com/auth/callback
```

---

## DigitalOcean (Producción)

### Opción 1: App Platform (Más fácil)

1. **Crear App en DigitalOcean**
2. **Conectar GitHub**
3. **Configuración**:
   - **Source**: GitHub repo
   - **Type**: Web Service
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080`

### Opción 2: Droplet (Más control)

1. **Crear Droplet Ubuntu 22.04**
2. **Configurar servidor**:

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install python3-pip python3-venv nginx -y

# Clonar proyecto
git clone https://github.com/tu-usuario/ads-checker.git
cd ads-checker

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Instalar Gunicorn
pip install gunicorn
```

3. **Crear archivo systemd**:
```bash
sudo nano /etc/systemd/system/ads-checker.service
```

```ini
[Unit]
Description=Ads Checker API
After=network.target

[Service]
User=root
WorkingDirectory=/root/ads-checker
Environment=PATH=/root/ads-checker/venv/bin
EnvironmentFile=/root/ads-checker/.env
ExecStart=/root/ads-checker/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Configurar Nginx**:
```bash
sudo nano /etc/nginx/sites-available/ads-checker
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. **Activar configuración**:
```bash
sudo ln -s /etc/nginx/sites-available/ads-checker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable ads-checker
sudo systemctl start ads-checker
```

6. **SSL con Certbot**:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

---

## Variables de Entorno para Producción

### Archivo `.env` para producción:
```env
# APIs
GOOGLE_ADS_API_KEY=tu_api_key_real
GOOGLE_ADS_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=tu_client_secret_real
GOOGLE_ADS_DEVELOPER_TOKEN=tu_developer_token_real
GOOGLE_ADS_REFRESH_TOKEN=tu_refresh_token_real

META_ADS_ACCESS_TOKEN=tu_access_token_real
META_ADS_APP_ID=tu_app_id_real
META_ADS_APP_SECRET=tu_app_secret_real

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Seguridad (opcional)
ALLOWED_HOSTS=tu-dominio.com,tu-app-name.onrender.com
```

---

## Checklist de Deployment

### Render ✅
- [ ] Repositorio en GitHub
- [ ] Proyecto creado en Render
- [ ] Variables de entorno configuradas
- [ ] Build y Start commands configurados
- [ ] OAuth URIs actualizadas en Google Cloud
- [ ] SSL automático (incluido en Render)

### DigitalOcean ✅
- [ ] Droplet o App creado
- [ ] Código deployado
- [ ] Variables de entorno configuradas
- [ ] Nginx configurado (solo Droplet)
- [ ] SSL configurado
- [ ] OAuth URIs actualizadas
- [ ] Dominio apuntando al servidor

---

## URLs finales

### Render:
- **API**: `https://tu-app-name.onrender.com`
- **Docs**: `https://tu-app-name.onrender.com/docs`

### DigitalOcean:
- **API**: `https://tu-dominio.com`
- **Docs**: `https://tu-dominio.com/docs`

---

## Testing después del deployment

```bash
# Test básico
curl https://tu-app-name.onrender.com/

# Test sin APIs
curl "https://tu-app-name.onrender.com/api/v1/no-api/analyze/nike.com"

# Test health check
curl "https://tu-app-name.onrender.com/api/v1/ads/health"
```