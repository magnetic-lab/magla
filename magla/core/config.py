"""Basic config reader for future config loading implementations."""
import os
import yaml
import json

from .errors import ConfigPathError, ConfigReadError


class MaglaConfig(object):
    """Provide an interface to multiple types of config filetypes.
    
    Supported types:
    ----------------
        - json
        - yaml
    """
    _loaders = {
        "json": json.load,
        "yaml": yaml.safe_load
    }
    _writers = {
        "json": json.dumps,
        "yaml": yaml.dump
    }
    def __init__(self, path):
        """Initialize with config path.

        Parameters
        ----------
        path : str
            Path to the config file
        """
        self._path = path
        self._config = self.load()

    @property
    def path(self):
        """Retrieve path to current instance's config json.

        Returns
        -------
        str
            The path to the associated config file
        """
        return self._path

    def clear(self):
        """Reset the prefs json to an empty dict and save."""
        self.save({})

    def get(self, key, default = None):
        """Get value by key from current instance's config.

        Parameters
        ----------
        key : str
            The key to retrieve
        default : *, optional
            Value to return if key was not found, by default None

        Returns
        -------
        *
            Value of given key
        """
        return self._config.get(key, default)

    def load(self):
        """Retrieve the contents of config.json and set to the current instance.

        Returns
        -------
        dict
            Python dict version of the loaded config file

        Raises
        ------
        ConfigReadError
            Thrown if the given config path was unreadable
        ConfigPathError
            Thrown if an invalid config path was given
        """
        config_dict = {}
        loader = self._get_loader()
        try:
            with open(self._path, "r") as config_fo:
                config_dict = loader(config_fo)
        except (FileNotFoundError, PermissionError, json.decoder.JSONDecodeError) as err:
            if isinstance(err, json.decoder.JSONDecodeError):
                raise ConfigReadError(err)
            raise ConfigPathError(err)

        self._config = config_dict

        return self._config

    def save(self, config_dict):
        """Apply given config_dict to disk and update isntance dict.

        Parameters
        ----------
        config_dict : dict
            The config dict to save to the loaded config file

        Returns
        -------
        dict
            The saved config dict

        Raises
        ------
        ConfigReadError
            Thrown if config file was unreadable
        ConfigPathError
            Thrown if path to the config file is invalid
        """
        writer = self._get_writer()
        try:
            with open(self._path, "w+") as config_fo:
                config_fo.write(writer(config_dict))
        except (FileNotFoundError, PermissionError, json.decoder.JSONDecodeError) as err:
            if isinstance(err, json.decoder.JSONDecodeError):
                raise ConfigReadError(err)
            raise ConfigPathError(err)

        self._config = config_dict

        return self._config

    def update(self, new_config_dict):
        """Update the instance dict.

        Parameters
        ----------
        new_config_dict : dict
            dictionary of preferences to update.

        Returns
        -------
        dict
            Dict of the config.
        """
        self._config.update(new_config_dict)
        return self._config
    
    def dict(self):
        """Retrieve config contents as a dict.

        Returns
        -------
        dict
            dict containing the contents of given config file.
        """
        return self._config

    def _get_loader(self):
        """Retrieve the correct adapter for loading.

        Returns
        -------
        function
            The filetype-specific function to be used to load contents.
        """
        config_type = os.path.splitext(self._path)[1].replace(".", "")
        return self._loaders[config_type]
    
    def _get_writer(self):
        """Retrieve the correct adapter for writing.

        Returns
        -------
        function
            The filetype-specific function to be used to write to the given config file.
        """
        config_type = os.path.splitext(self._path)[1].replace(".", "")
        return self._writers[config_type]