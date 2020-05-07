# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""
import os
import time
import codecs
from datetime import datetime
from flask_login import current_user

def _kb_size(size):
    return '%.2f Kb' %(size/1024)

def _standard_timestr(localtime):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(localtime))


_TEXT_BOMS = (
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
    codecs.BOM_UTF8,
)

def _is_dir(node_path):
    return os.path.isdir(node_path)

def _is_audio_file(node_path):
    path, filename = os.path.split(node_path)
    suffix = filename.split('.')[-1]
    if suffix in ['mp3', 'wav']:
        return True
    return False

def _is_video_file(node_path):
    path, filename = os.path.split(node_path)
    suffix = filename.split('.')[-1]
    if suffix in ['mp4']:
        return True
    return False

def _is_binary_file(node_path):
    with open(node_path, 'rb') as file:
        initial_bytes = file.read(8192)
        file.close()
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) and b'\0' in initial_bytes

class NodeType(object):
    __register__ = list()
    
    def __init__(self, name, cond=None):
        self.id = len(NodeType.__register__)
        self.name = name
        self.condition = lambda path:True
        if cond:
            self.condition = cond
        NodeType.__register__.append(self)
 
    @classmethod
    def register(cls):
        return cls.__register__
    
    def __eq__(self, obj):
        return self.id == obj.id

    def __repr__(self):
        return "Object '%s'[id=%d, name='%s']"%(self.__class__.__name__, self.id, self.name)

class NodeTypes(object):
    Directory = NodeType('Directory', cond=_is_dir)
    AudioFile = NodeType('Audio File', cond=_is_audio_file)
    VideoFile = NodeType('Video File', cond=_is_video_file)
    BinaryFile = NodeType('Binary File', cond=_is_binary_file)
    TextFile = NodeType('Text File')

    @classmethod
    def NodeType(cls, node_path):
        try:
            for ndt in NodeType.register():
                if ndt.condition(node_path):
                    return ndt
        except:
            return dict(id=-1, name='Unknow Type')

class Node(object):
    def __init__(self, path):
        """ Initialize node object with attributes.
            `path`: web path such as '/', '/home', '/home/data'
            `name`: node name root path name is 'Home'
            `local_path`: the full path of node in server.
        """
        self.owner = current_user
        self.path = self._rectify(path)
        if self.path == '/':
            self._set_base_use_default()
        else:
            self.name = self.path.split('/')[-1]
            self.local_path = os.path.join(self.owner.home, self.path[1:].replace('/', os.path.sep))
        
        if not os.path.exists(self.local_path):
            self._set_base_use_default()
        self._set_extra()

    def _rectify(self, path):
        """ Return regulated path.
            rectify input path to regular path such as '/','/home', '/home/data'
        """
        if path is None or path == '':
            path = '/'
        if path == '/':
            return path
        if not path[0] == '/':
            path = '/' + path
        if path[-1:] == '/':
            path = path[:-1]
        return path
    
    def _set_base_use_default(self):
        """ Set base attr with default value.
            base attrs: `path`, `name`, `local_path`
        """
        self.path = '/'
        self.name = 'Home'
        self.local_path = self.owner.home

    def _set_extra(self):
        """ Set extra attributes after set `local_path`
        """
        node_info = os.stat(self.local_path)
        self.size = _kb_size(node_info.st_size)
        self.create = _standard_timestr(node_info.st_ctime)
        self.visit = _standard_timestr(node_info.st_atime)
        self.modify = _standard_timestr(node_info.st_mtime)
        self.type = NodeTypes.NodeType(self.local_path)
        self.is_dir = self.type == NodeTypes.Directory

    @property
    def layer_path(self):
        paths = list()
        if self.path == '/':
            paths.append(dict(name='Home', path='/'))
            return paths
        path_names = self.path.split('/')
        for i in range(len(path_names)):
            _name = path_names[i]
            if i == 0:
                paths.append(dict(name='Home', path='/'))
            else:
                d = dict(name=_name, path='/'.join(path_names[:i+1]))
                paths.append(d)
        return paths

    @property
    def children(self):
        """ Return children node list.
        """
        child_list = list()
        for _name in os.listdir(self.local_path):
            if self.path == '/':
                path = '/' + _name
            else:
                path = self.path + '/' + _name
            node = Node(path)
            child_list.append(node)
        return child_list
    
    @property
    def tree(self):
        node_tree = list()
        node_tree.append(dict(id=self.path, parent="#", text=self.name, state=dict(opened=True)))
        for root, dirs, files in os.walk(self.local_path):
            for dname in dirs:
                _suffix = root[len(self.local_path):].replace(os.path.sep, '/')
                _parent = self.path + '/' + _suffix
                if _suffix == '':
                    _parent = self.path
                else:
                    if self.path =='/':
                        _parent = _suffix
                    else:
                        _parent = self.path + _suffix

                if _parent == '/':
                    _path = '/' + dname
                else:
                    _path = _parent + '/' + dname
                d = dict(id=_path, parent=_parent, text=dname)
                node_tree.append(d)
        return node_tree