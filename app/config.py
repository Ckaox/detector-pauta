# Configuración para deployment en producción
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # APIs
    GOOGLE_ADS_API_KEY = os.getenv("GOOGLE_ADS_API_KEY")
    GOOGLE_ADS_CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
    GOOGLE_ADS_CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
    GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    GOOGLE_ADS_REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
    
    META_ADS_ACCESS_TOKEN = os.getenv("META_ADS_ACCESS_TOKEN")
    META_ADS_APP_ID = os.getenv("META_ADS_APP_ID")
    META_ADS_APP_SECRET = os.getenv("META_ADS_APP_SECRET")
    
    # Servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Seguridad
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else ["*"]
    
    # URLs base según el entorno
    @property
    def BASE_URL(self):
        if self.DEBUG:
            return f"http://{self.HOST}:{self.PORT}"
        else:
            # Detectar si estamos en Render o DigitalOcean
            render_url = os.getenv("RENDER_EXTERNAL_URL")
            if render_url:
                return render_url
            return f"https://{os.getenv('DOMAIN', 'localhost')}"

settings = Settings()