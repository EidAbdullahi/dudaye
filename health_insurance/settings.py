"""
Django settings for health_insurance project.

Enhanced and structured configuration for Django 4.2+
"""

from pathlib import Path
import os
from datetime import timedelta

# ----------------------------
# Base directory
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ----------------------------
# Security
# ----------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-zh)q)o4&m)57i6!whqr^#@&(kf_%tc3i+o7-+kp38!!0m^dcjk"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Allow all during local dev — restrict in production
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "0.0.0.0,127.0.0.1,localhost"
).split(",")


# ----------------------------
# Applications
# ----------------------------
INSTALLED_APPS = [
    # Core Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",

    # Third-party apps
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",  # ✅ Allow CORS for frontend connections (React/Vue etc.)

    # Local apps
    "accounts",
    "clients",
    "policies",
    "claims",
    "hospitals",

]


# ----------------------------
# Middleware
# ----------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be at the top
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # ✅ Enable CORS before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ----------------------------
# URLs and WSGI
# ----------------------------
ROOT_URLCONF = "health_insurance.urls"
WSGI_APPLICATION = "health_insurance.wsgi.application"


# ----------------------------
# Database
# ----------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ----------------------------
# Authentication
# ----------------------------
AUTH_USER_MODEL = "accounts.User"

# Optional: DRF Token expiration support
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
}

# JWT Authentication (optional future upgrade)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}


# ----------------------------
# CORS (for API Frontend)
# ----------------------------
CORS_ALLOW_ALL_ORIGINS = True  # ✅ For local testing only
# For production:
# CORS_ALLOWED_ORIGINS = ["https://your-frontend-domain.com"]


# ----------------------------
# Password validation
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ----------------------------
# Internationalization
# ----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"  # ✅ Better default for Kenya/East Africa
USE_I18N = True
USE_TZ = True


# ----------------------------
# Static & Media Files
# ----------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ----------------------------
# Templates
# ----------------------------
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ this must point to your root templates folder
        'APP_DIRS': True,                  # ✅ enables app templates too
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]




# ----------------------------
# Logging (optional but useful)
# ----------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


# ----------------------------
# Default primary key type
# ----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Redirect after login/logout


LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/clients/login/'

