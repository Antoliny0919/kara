import dj_database_url
from django.core.files.storage import FileSystemStorage

from .base import *

# LANGUAGE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
DEBUG = False

LANGUAGE_CODE = "en-us"

SECRET_KEY = "TEST**123456789**TEST"

DATABASES["default"] = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
)

# MEDIA
# ------------------------------------------------------------------------------
MEDIA_URL = "test_media/"

MEDIA_ROOT = "test_media/"


# STORAGE
# ------------------------------------------------------------------------------
class CustomTestFileSystemStorage(FileSystemStorage):
    """
    In the test environment, the storage overwrites the file
    and does not use a hash in the file name.
    """

    def get_available_name(self, name, max_length=None):
        return name

    def save(self, name, content, max_length=None):
        if self.exists(name):
            self.delete(name)
        return super().save(name, content, max_length)


STORAGES = {
    "default": {
        "BACKEND": "config.settings.test.CustomTestFileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

LOGGING = {}
