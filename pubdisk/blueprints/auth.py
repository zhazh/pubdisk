# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

from flask import current_app, render_template, redirect, url_for, Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from pubdisk.extensions import db
from pubdisk.blueprints import login_redirect, user_required
from pubdisk.forms import LoginForm, ChangePasswordForm
from pubdisk.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@login_redirect
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if User.check(form.username.data, form.password.data):
            user = User.query.filter(User.name == form.username.data).first()
            login_user(user, remember=form.remember_me.data)
            if user.role_admin:
                return redirect(url_for('admin.index'))
            else:
                next = request.args.get('next')
                return redirect(next or url_for('users.main'))
        else:
            form.username.errors.append("Incorrect username or password")
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# used by ajax method
@auth_bp.route('/change-password', methods=['POST'])
@user_required('json')
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            if current_user.equal_password(form.old_password.data):
                current_user.set_password(form.new_password.data)
                db.session.commit()
                logout_user()
            else:
                return jsonify(dict(code=1, msg='Incorrect old password.'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning("User[%r] change_password occurred an error:%s"%(current_user, str(e)))
            return jsonify(dict(code=2, msg='Database exception.'))
    else:
        msg = ''
        for field, errors in form.errors.items():
            msg = "'%s':"%field
            for error in errors:
                msg = msg + ' ' + error
        if msg != '':
            return jsonify(dict(code=3, msg=msg))
    return jsonify(dict(code=0, msg='Success'))
