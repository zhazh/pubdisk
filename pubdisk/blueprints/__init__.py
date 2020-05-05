# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

from flask import redirect, url_for, jsonify, abort
from flask_login import current_user
from functools import wraps

from pubdisk.extensions import login_manager

_login_view = 'auth.login'
_users_view = 'users.main'
_admin_view = 'admin.index'

def login_redirect(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if current_user.is_authenticated:
            if current_user.role_admin:
                return redirect(url_for(_admin_view))
            else:
                return redirect(url_for(_users_view))
        return func(*args, **kw)
    return wrapper

def user_required(ret_type):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kw):
            if not current_user.is_authenticated:
                if ret_type == 'json':
                    return jsonify(code=100, msg='Unauthenticated user.')
                else:
                    abort(401)
            return func(*args, **kw)
        return wrapper
    return outer

def admin_required(ret_type):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kw):
            if current_user.is_authenticated:
                if not current_user.role_admin:
                    if ret_type == 'json':
                        return jsonify(dict(code=101, msg='Permission denied.'))
                    return redirect(url_for(_users_view))
                # admin user.
                return func(*args, **kw)
            # user unauthenticated.
            if ret_type == 'json':
                return jsonify(dict(code=100, msg='Unauthenticated user.'))
            return redirect(url_for(login_manager.login_view))
        return wrapper
    return outer

from .auth import auth_bp
from .users import users_bp
from .admin import admin_bp