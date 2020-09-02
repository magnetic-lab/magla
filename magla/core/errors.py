"""Root exception definitions for `magla` as well as associated logging logic."""
import logging


class MaglaError(Exception):
    """Base Exception class.
    :attr msg: message str given from raiser.
    :type msg: str
    """
    def __init__(self, message, *args, **kwargs):
        """Initialize with message str.
        :param msg: message describing exception from raiser.
        """
        super(MaglaError, self).__init__(*args, **kwargs)
        self.message = message
        logging.error(self.__str__())

    def __str__(self):
        return "<{error}: {msg}>".format(error=self.__class__.__name__, msg=self.message)


class ConfigPathError(MaglaError):
    """Unable to read from the given filepath."""


class ConfigReadError(MaglaError):
    """Unable to parse contents of config to dict."""
