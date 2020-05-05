# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

import os
from flask import (
        render_template, redirect, url_for, request, jsonify, abort,
        Blueprint, current_app, send_from_directory, make_response
)
from flask_login import login_user, logout_user, login_required, current_user

from pubdisk.extensions import db
from pubdisk.blueprints import login_redirect, user_required
from pubdisk.utils import Node, NodeTypes

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_redirect
def index():
    return redirect(url_for('auth.login'))

#: main page will load other page by ajax get method.
@users_bp.route('/main')
@login_required
def main():
    return render_template('users/main.html')

# get by ajax method
@users_bp.route('/home', methods=["GET"])
@user_required('html')
def home():
    path = request.args.get('path', '/')
    node = Node(path)
    return render_template('users/_home.html', paths=node.layer_path, node_list=node.children)

@users_bp.route('/download', methods=["GET"])
@user_required('html')
def download():
    path = request.args.get('path', '/')
    node = Node(path)
    if not os.path.exists(node.local_path) or not os.path.isfile(node.local_path):
        abort(400)
    _path, _filename = os.path.split(node.local_path)
    current_app.logger.info('download: path:%s, filename=%s'%(_path, _filename))
    response = make_response(send_from_directory(_path, filename=_filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(_filename.encode().decode('latin-1'))
    return response

# get by ajax method
@users_bp.route('/tree', methods=['GET'])
@user_required('json')
def tree():
    path = request.args.get('path', '/')
    node = Node(path)
    return jsonify(node.tree)

# get by ajax method
@users_bp.route('/search', methods=['GET'])
@user_required('html')
def search():
    node_list = list()
    keywords = request.args.get('keywords', None)
    if keywords is None:
        return render_template('users/_search.html', keywords='', node_list=node_list)
    _keywords = list(filter(lambda s:len(s)>0, keywords.split()))
    for root, dirs, files in os.walk(current_user.home):
        for fname in files:
            for keyword in _keywords:
                if fname.find(keyword) != -1:
                    _suffix = root[len(current_user.home):].replace(os.path.sep, "/")
                    _dir = '/' if _suffix == '' else _suffix
                    _path = _dir + fname if _dir == '/' else _dir + '/' + fname
                    d = dict(name=fname, dir=_dir, path=_path)
                    node_list.append(d)
    return render_template('users/_search.html', keywords=keywords, node_list=node_list)
