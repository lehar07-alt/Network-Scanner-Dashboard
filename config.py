import os
from dotenv import load_dotenv

# Find the absolute path to the project's root folder
basedir = os.path.abspath(os.path.dirname(__file__))

# Load variables from .env into the environment
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration shared by all environments."""

    # Used by Flask to sign session cookies and CSRF tokens — must be secret
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-key-do-not-use-in-prod')

    # Where our SQLite database file lives
    DB_PATH = os.path.join(basedir, 'database', 'app.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + DB_PATH
    )

    # Disables a feature we don't need, and it saves memory + removes a warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings (used starting Section 12)
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')