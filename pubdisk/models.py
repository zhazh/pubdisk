# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

import os
from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, func, exists, and_, or_
from pubdisk.extensions import db


class User(db.Model):
    """ User table.
        Attributes:
            hash_passwd:	encrypted user password.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, unique=True)
    hash_passwd = db.Column(db.String(128))
    dt_create = db.Column(db.DateTime, default=datetime.utcnow)
    home = db.Column(db.String(256))
    role_admin = db.Column(db.Boolean, default=False)

    def __init__(self, **kw):
        if set(['name', 'password']) <= set(kw.keys()):
            kw['hash_passwd'] = generate_password_hash(kw['password'])
            kw.pop('password')
            self.set_home(kw.get('home', current_app.config.get('USERS_ROOT')))
            super(User, self).__init__(**kw)
        else:
            raise TypeError("Miss argument 'name' or 'password'.")

    # rewrite equal function.
    def __eq__(self, other):
        if type(other) == type(self):
            return self.id == other.id
        return False
    
    # rewrite not equal function.
    def __ne__(self, other):
        return not self.__eq__(other)
    
    # rewrite string function.
    def __repr__(self):
        return 'User[id:%d,name:%s, home:%s, role_admin:%r]'%(self.id, self.name, self.home, self.role_admin)
    
    @classmethod
    def check(cls, name, password):
        """ Check login by username and password
            :returns: boolean.
        """
        usr = cls.query.filter_by(name=name).first()
        if usr:
            return check_password_hash(usr.hash_passwd, password)
        return False

    def equal_password(self, password):
        return check_password_hash(self.hash_passwd, password)
    
    def set_password(self, password):
        self.hash_passwd = generate_password_hash(password)

    def set_home(self, home):
        try:
            self.home = home
            if not os.path.exists(self.home):
                os.makedirs(self.home)
        except:
            raise ValueError("home:[%s] cann't build."%home)

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)
