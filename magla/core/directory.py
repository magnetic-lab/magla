# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os

from .errors import MaglaError
from .data import MaglaData
from .entity import MaglaEntity
from .user import MaglaUser

from ..utils import open_directory_location
from ..db.directory import Directory

try:
    basestring
except NameError:
    basestring = str

class MaglaDirectoryError(MaglaError):
    """An error accured preventing MaglaDirectory to continue."""


class MaglaDirectory(MaglaEntity):
    """"""
    SCHEMA = Directory

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaDirectory, self).__init__(self.SCHEMA, data or dict(kwargs))
        
    def __repr__(self):
        return self.path
    
    def __str__(self):
        return self.__repr__()

    @property
    def id(self):
        return self.data.id
    
    @property
    def label(self):
        return self.data.label
    
    @property
    def path(self):
        return self.data.path
    
    @property
    def tree(self):
        return self.data.tree

    #### SQAlchemy relationship back-references
    @property
    def machine(self):
        r = self.data.record.machine
        if not r:
            return None
        return self.from_record(r)

    @property
    def user(self):
        r = self.data.record.user
        if not r:
            return None
        return self.from_record(r)

    # MaglaDirectory-specific methods ______________________________________________________________
    def open(self):
        open_directory_location(self.path)
        
    def make_tree(self):
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        self._recursive_make_tree(self.path, self.tree or [])
                
    def _recursive_make_tree(self, root, sub_tree):
        for dict_ in sub_tree:
            k, v = list(dict_.items())[0]
            abs_path = os.path.join(root, k)
            print("making: {}".format(abs_path))
            try:
                os.makedirs(abs_path, exist_ok=False)
            except OSError as e:
                if e.errno == 17:  # `FileExistsError`
                    continue
            if v:
                self._recursive_make_tree(root=os.path.join(root, k), sub_tree=v)
        