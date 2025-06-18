import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LTI_KEY = os.environ.get('LTI_KEY') or 'default_key'
    LTI_SECRET = os.environ.get('LTI_SECRET') or 'default_secret'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'