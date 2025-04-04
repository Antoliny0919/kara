import dj_database_url

from .base import *

# LANGUAGE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"

SECRET_KEY = "TEST**123456789**TEST"

DATABASES["default"] = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
)
