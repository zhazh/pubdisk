# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

import os
import click
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from pubdisk.models import User
from pubdisk.settings import config
from pubdisk.extensions import (db, login_manager, migrate, csrf)
from pubdisk.blueprints import auth_bp, users_bp, admin_bp
from pubdisk.utils import NodeTypes

__author__ = "zhazh"
__version__ = ".".join(["0", "0", "1"])

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "production")
    app = Flask("pubdisk")
    app.config.from_object(config[config_name])

    register_logger(app)
    register_extensions(app)
    register_template_context(app)
    register_errors(app)
    register_blueprints(app)
    register_commands(app)
    return app

def register_logger(app):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/pubdisk.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    if not app.debug:
        app.logger.addHandler(file_handler)

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        return dict(brand_name=app.config.get('BRAND_NAME'), NodeTypes=NodeTypes)

def register_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning('404 - full_path: %s'%request.full_path)
        return render_template('errors/error.html', error=e), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.warning('500 - full_path: %s'%request.full_path)
        return render_template('errors/error.html', error=e), 500
    
    @app.errorhandler(CSRFError)
    def handler_csrf_error(e):
        # handle csrf protect error.
        app.logger.warning('400 - full_path: %s, description:%s'%(request.full_path, e.description))
        return render_template('errors/error.html', error=e), 400
    
def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """ Initialize the database. """
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo("Initialized database.")

    @app.cli.command()
    def init():
        """ Building pubdisk """
        db.create_all()
        click.echo("Initialized database.")
        _name = "admin"
        _password = "admin"
        admin = User.query.filter(User.role_admin == True).first()
        if admin is None:
            admin = User(name=_name, password=_password, role_admin=True)
            db.session.add(admin)
            click.echo("Created the administrator, username:[%s], password:[%s]"%(_name, _password))
        else:
            admin.name = _name
            admin.set_password(_password)
            click.echo("Updating the administrator, username:[%s], password:[%s]"%(_name, _password))
        db.session.commit()
        click.echo("Done.")

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def add_user(username, password):
        """ Create a normal account. """
        db.create_all()
        click.echo("Initialized database.")
        user = User(name=username, password=password)
        db.session.add(user)
        db.session.commit()
        click.echo("Done.")
