import subprocess
import logging

from .tool import MaglaTool

logging.basicConfig(level=logging.INFO)


def start(*args):

    for i, tool_name in enumerate(args):

        # skip integers
        if tool_name.isdigit():
            continue

        tool = MaglaTool(tool_name)
        ver = None
        if tool:
            # check if the next item is an int
            if i < len(args) - 1 and args[i + 1].isdigit():
                # if it is set the version
                ver = args[i + 1]

            tool.start(ver)


def __parse_int(str_):

    try:
        return int(str_)

    except ValueError:
        return str_
