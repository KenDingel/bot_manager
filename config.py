import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN') or 'default-token'
    BOTS = ['bot1', 'bot2', 'bot3']  # Replace with your actual bot names