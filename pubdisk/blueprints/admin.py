# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

from flask import render_template, redirect, url_for, Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from pubdisk.models import User
from pubdisk.extensions import db
from pubdisk.forms import NewUserForm
from pubdisk.blueprints import admin_required, admin_required
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_required('html')
def index():
    users = User.query.filter(User.role_admin == False).all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/new_user', methods=['POST'])
@admin_required('json')
def new_user():
    form = NewUserForm()
    if form.validate_on_submit():
        username = form.username.data
        userhome = form.userhome.data
        root = current_app.config.get('USERS_ROOT')
        localhome = os.path.join(root, userhome[1:].replace('/', os.path.sep))
        try:
            default_passwd = current_app.config.get('USERS_PASSWORD')
            user = User(name=username, password=default_passwd, home=localhome, role_admin=False)
            db.session.add(user)
            db.session.commit()
            return jsonify(dict(code=0, msg=default_passwd))
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning('create new user failed:', str(e))
            return jsonify(dict(code=1, msg='Name:%s has exists'%username))
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning('create new user failed:', str(e))
            return jsonify(dict(code=2, msg=str(e)))
    else:
        msg = ''
        for field, errors in form.errors.items():
            msg = "'%s':"%field
            for error in errors:
                msg = msg + ' ' + error
        if msg != '':
            return jsonify(dict(code=3, msg=msg))
    return jsonify(dict(code=0, msg=''))

@admin_bp.route('/del_user', methods=['POST'])
@admin_required('json')
def del_user():
    user_id = request.form.get('user_id', None)
    if user_id is None:
        return jsonify(dict(code=1, msg='Argument user_id missed.'))
    user = User.query.filter(User.id==user_id).first()
    if user is None:
        return jsonify(dict(code=2, msg='User not found.'))
    if user.id == current_user.id:
        return jsonify(dict(code=3, msg='Can not delete yourself.'))
    if user.role_admin:
        return jsonify(dict(code=4, msg='Can not delete an adminstrator account.'))
    
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning('del_user occurred an error:', str(e))
        return jsonify(dict(code=5, msg='Database exception'))
    return jsonify(dict(code=0, msg='Success'))

@admin_bp.route('/reset_password', methods=['POST'])
@admin_required('json')
def reset_password():
    default_passwd = current_app.config.get('USERS_PASSWORD')
    user_id = request.form.get('user_id', None)
    if user_id is None:
        return jsonify(dict(code=1, msg='Argument user_id missed.'))
    user = User.query.filter(User.id==user_id).first()
    if user is None:
        return jsonify(dict(code=2, msg='User not found.'))
    if user.id == current_user.id:
        return jsonify(dict(code=3, msg='Can not reset yourself password.'))
    if user.role_admin:
        return jsonify(dict(code=4, msg='Can not reset an adminstrator password.'))
    
    try:
        user.set_password(default_passwd)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning('reset_password occurred an error:', str(e))
        return jsonify(dict(code=5, msg='Database exception'))
    return jsonify(dict(code=0, msg=default_passwd))