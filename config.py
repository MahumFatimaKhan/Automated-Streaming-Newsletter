import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration settings."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FLUX_API_KEY = os.getenv('FLUX_API_KEY')
    FLUX_API_URL = os.getenv('FLUX_API_URL', 'https://api.flux.ai/v1/generate')
    
    # Scraping settings
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', 30))
    HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true'
    TVINSIDER_BASE_URL = 'https://www.tvinsider.com/shows/calendar/'
    SCRAPE_METHOD = os.getenv('SCRAPE_METHOD', 'date_range')  # 'date_range' or 'full_page'
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 900))
    
    # Rate limiting
    OPENAI_RATE_LIMIT = int(os.getenv('OPENAI_RATE_LIMIT', 60))
    API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', 3))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', 2))
    
    # Content generation settings
    TAGLINE_MIN_LENGTH = 50
    TAGLINE_MAX_LENGTH = 80
    INTRO_MIN_LENGTH = 100
    INTRO_MAX_LENGTH = 200
    
    # Image settings
    BANNER_WIDTH = 1200
    BANNER_HEIGHT = 400
    IMAGE_QUALITY = 95
    
    # File paths
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    ASSETS_FOLDER = os.path.join(STATIC_FOLDER, 'assets')
    TEMP_FOLDER = 'temp'
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            if not cls.DEBUG:
                errors.append("SECRET_KEY must be set in production")
        
        return errors