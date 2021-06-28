# -*- coding: utf-8 -*-
"""Directories give `magla` an interface to interact with directory-structures and their contents.

There should never be any hard-coded paths anywhere except by users via settings. If something
relies on accessing local directories then a `MaglaDirectory` record must first be created and
associated.
"""
import os
import shutil
import sys

from ..db.directory import Directory
from ..utils import open_directory_location
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaDirectoryError(MaglaError):
    """An error accured preventing MaglaDirectory to continue."""


class MaglaDirectory(MaglaEntity):
    """Provide an interface for interacting with local filesystem.

    `MaglaDirectory` objects are intended to represent a root location and encompass all children
    contained within rather than behaving in a hierarchal fashion.

    Structure of a `MaglaDirectory` object:

        label
        -----
            A descriptive comment about this directory

        path
        ----
            The path to the root of the directory

        tree
        ----
            A description of a directory tree using nested dicts and lists

            example:
                ```
                [
                    {"shots": []},
                    {"audio": []},
                    {"preproduction": [
                        {"mood": []},
                        {"reference": []},
                        {"edit": []}]
                    }
                ]
                ```

            results in following tree-structure:
                ```
                shots
                audio
                preproduction
                    |_mood
                    |_reference
                    |_edit
                ```

        bookmarks
        ---------
            A dictionary to store locations within the directory (such as executeables, configs, etc).
            Python string formatting can be utilized as shown below.

            example:
            ```
            shot_version_bookmarks = {
                "ocio": "_in/color/{shot_version.full_name}.ocio",
                "luts": "_in/color/luts",
                "representations": {
                    "png_sequence": "_out/png/{shot_version.full_name}.####.png",
                    "youtube_mov": "_out/png/{shot_version.full_name}.mov",
                    "exr_sequence": "_out/png/{shot_version.full_name}.####.exr"
                }
            ```
    """
    __schema__ = Directory

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict, optional
            Data to query for matching backend record
        """
        super(MaglaDirectory, self).__init__(data or dict(kwargs))

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.__repr__()

    @property
    def id(self):
        """Retrieve id from data.

        Returns
        -------
        int
            Postgres column id
        """
        return self.data.id

    @property
    def label(self):
        """Retrieve label from data.

        Returns
        -------
        str
            Postgres column label
        """
        return self.data.label

    @property
    def path(self):
        """Retrieve path from data.

        Returns
        -------
        str
            Postgres column path
        """
        return self.data.path

    @property
    def tree(self):
        """Retrieve tree from data.

        Returns
        -------
        dict
            Postgres column tree (JSONB)
        """
        return self.data.tree

    @property
    def bookmarks(self):
        """Retrieve bookmarks from data.

        Returns
        -------
        dict
            Postgres column bookmarks (JSONB)
        """
        return self.data.bookmarks

    # SQAlchemy relationship back-references
    @property
    def machine(self):
        """Retrieve related `MaglaMachine` back-reference.

        Returns
        -------
        magla.core.machine.MaglaMachine
            The `MaglaMachine` this directory exists on
        """
        r = self.data.record.machine
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def user(self):
        """Retrieve related `MaglaUser` back-reference.

        Returns
        -------
        magla.core.user.MaglaUser
            The `MaglaUser` owner if any
        """
        r = self.data.record.user
        if not r:
            return None
        return MaglaEntity.from_record(r)

    # MaglaDirectory-specific methods ______________________________________________________________
    def bookmark(self, name):
        """Retrieve and convert given bookmark to absolute path.
        Parameters
        ----------
        name : str
            The bookmark key name
        Returns
        -------
        str
            The absolute path of the bookmark, or the if it does not exist an absolute path is
            created using the name as the relative path.
        """
        return os.path.join(self.path, self.bookmarks.get(name, name))

    def open(self):
        """Open the directory location in the os file browser."""
        open_directory_location(self.path)

    def make_tree(self):
        """Create the directory tree on the machine's filesystem."""
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        self._recursive_make_tree(self.path, self.tree or [])

    def bookmark(self, name):
        """Retrieve and convert given bookmark to absolute path.

        Parameters
        ----------
        name : str
            The bookmark key name

        Returns
        -------
        str
            The absolute path of the bookmark, or the if it does not exist an absolute path is
            created using the name as the relative path.
        """
        return os.path.join(self.path, self.bookmarks.get(name, name))

    def _recursive_make_tree(self, root, sub_tree):
        """Recursively create the directory tree.

        Parameters
        ----------
        root : str
            The root directory of the current recursion loop.
        sub_tree : list
            The nested directies if any
        """
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

    def delete_tree(self):
        try:
            shutil.rmtree(self.path)
        except OSError:
            raise
        sys.stdout.write("Deleted directory tree at: '{0}'".format(self.path))
