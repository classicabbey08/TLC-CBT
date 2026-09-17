"""
Django settings for the CBT System project.
"""

from pathlib import Path

from decouple import config, Csv
import dj_database_url


# =========================
# BASE DIRECTORY
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY
# =========================

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-key-change-me",
)

DEBUG = config(
    "DEBUG",
    default=True,
    cast=bool,
)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,.onrender.com",
    cast=Csv(),
)


# =========================
# INSTALLED APPS
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "widget_tweaks",

    # Local apps
    "accounts",
    "exams",
    "attempts",
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URL CONFIGURATION
# =========================

ROOT_URLCONF = "cbt_system.urls"


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================
# WSGI
# =========================

WSGI_APPLICATION = "cbt_system.wsgi.application"


# =========================
# DATABASE
# =========================

# Local development:
#     SQLite
#
# Render/production:
#     PostgreSQL through DATABASE_URL

DATABASE_URL = config(
    "DATABASE_URL",
    default="",
)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# PASSWORD VALIDATION
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =========================
# CUSTOM USER MODEL
# =========================

AUTH_USER_MODEL = "accounts.User"


# =========================
# INTERNATIONALIZATION
# =========================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================
# STATIC & MEDIA FILES
# =========================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================
# DEFAULT PRIMARY KEY
# =========================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# LOGIN / LOGOUT
# =========================

LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "accounts:dashboard_redirect"

LOGOUT_REDIRECT_URL = "accounts:login"


# =========================
# CSRF / RENDER
# =========================

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://*.onrender.com",
    cast=Csv(),
)

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


# =========================
# INITIAL SUPER ADMIN
# =========================

INITIAL_SUPERUSER_USERNAME = config(
    "INITIAL_SUPERUSER_USERNAME",
    default="",
)

INITIAL_SUPERUSER_EMAIL = config(
    "INITIAL_SUPERUSER_EMAIL",
    default="",
)

INITIAL_SUPERUSER_PASSWORD = config(
    "INITIAL_SUPERUSER_PASSWORD",
    default="",
)


# =========================
# INITIAL TEACHER
# =========================

INITIAL_TEACHER_USERNAME = config(
    "INITIAL_TEACHER_USERNAME",
    default="",
)

INITIAL_TEACHER_EMAIL = config(
    "INITIAL_TEACHER_EMAIL",
    default="",
)

INITIAL_TEACHER_FIRST_NAME = config(
    "INITIAL_TEACHER_FIRST_NAME",
    default="Teacher",
)

INITIAL_TEACHER_LAST_NAME = config(
    "INITIAL_TEACHER_LAST_NAME",
    default="",
)

INITIAL_TEACHER_PASSWORD = config(
    "INITIAL_TEACHER_PASSWORD",
    default="",
)