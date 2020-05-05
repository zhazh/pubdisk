# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""
import os
import sys

_win = sys.platform.startswith("win")
if _win:
    _prefix = "sqlite:///"
else:
    _prefix = "sqlite:////"

_default_password = "123456"
_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "pubdisk-development.secret#key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # users settings.
    BRAND_NAME = os.getenv("BRAND_NAME", "Pubdisk")
    USERS_ROOT = os.getenv("USERS_ROOT", os.path.expanduser("~"))
    USERS_PASSWORD = os.getenv("USERS_PASSWORD", _default_password)


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = _prefix + os.path.join(_basedir, "data-dev.db")

class TestingConfig(BaseConfig):
    WTF_CSRF_ENABLED = False # Default value is True, Close it for testing.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database.

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", _prefix + os.path.join(_basedir, "data.db"))

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


