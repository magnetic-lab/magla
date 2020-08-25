"""This script simulates launching magla in a controlled production environment.

Before running magla Flask server or Client it is expected that:
    - the magla module is available in PYTHONPATH
    - environment variable MAGLA_CONFIG is set as a valid path to a json config (see README)

This scripts automates the above tasks then launches the given python target.

Default logging directory: ./logging_output
Default client ui: ./magla_client/ui.py
"""
import argparse
import os
import platform
import subprocess
import yaml

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class MaglaLauncherError(Exception):
    """Base Exception class."""

    def __init__(self, *args, **kwargs):
        """Initialize with message str.

        :param msg: message describing exception from raiser.
        """
        super(MaglaLauncherError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<{error}: {msg}>".format(error=self.__class__.__name__, msg=self.message)


class InvalidConfigPathError(MaglaLauncherError):
    """MAGLA_CONFIG env variable not set or is invalid."""


class InvalidLoggingOutputDirError(MaglaLauncherError):
    """magla_LOGGING_OUTPUT_DIR env variable not set or is invalid."""


class InvalidPython3AliasError(MaglaLauncherError):
    """Argument given for python3 alias was invalid or not given."""

def main(target):
    """Launch client and server apps with pythonpath injection and environment variables.

    :param target: int representing server/client (0: server, 1: client).
    """
    env = os.environ.copy()
    env["MAGLA_FACILITY_REPO"] = os.path.join(
        os.path.normpath(os.path.join(CURRENT_DIR, os.pardir)), "magla_facility_repo")
    # validate file exists
    if not os.path.isdir(env["MAGLA_FACILITY_REPO"]):
        raise InvalidConfigPathError(
            "The 'MAGLA_FACILITY_REPO' env variable: {0} doesn't exist or is not a directory.".format(
                env["MAGLA_FACILITY_REPO"]))

    env["MAGLA_CONFIG"] = os.path.join(
        env["MAGLA_FACILITY_REPO"], "config", "config.yaml")
    # validate file exists
    if not os.path.isfile(env["MAGLA_CONFIG"]):
        raise InvalidConfigPathError(
            "The 'MAGLA_CONFIG' env variable: {0} doesn't exist or is not a file.".format(
                env["MAGLA_CONFIG"]))

    env["MAGLA_PATHS"] = os.path.join(
        env["MAGLA_FACILITY_REPO"], "config", "paths.yaml")
    # validate file exists
    if not os.path.isfile(env["MAGLA_PATHS"]):
        raise InvalidConfigPathError(
            "The 'MAGLA_PATHS' env variable: {0} doesn't exist or is not a file.".format(
                env["MAGLA_PATHS"]))

    # inject dependencies
    dependencies = os.pathsep.join(
        [
            CURRENT_DIR,
            os.path.join(os.path.dirname(CURRENT_DIR), "maglapath")
        ]
    )
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = os.pathsep.join([env["PYTHONPATH"], dependencies])
    else:
        env["PYTHONPATH"] = dependencies

    return launch_target(target, env)

def launch_target(target, env):
    """Launch target with current directory appended to PYTHONPATH.

    :param target: int representing server/client (0: server, 1: client).
    :param env: dictionary containing environment variables to inject.
    :param config: MaglaConfig instance.
    """
    config = None
    with open(env["MAGLA_CONFIG"]) as config_fo:
        config = yaml.load(config_fo, yaml.SafeLoader)
    python_path = config.get("python_{system}".format(system=platform.system().lower()))

    if target == 0:
        # start server
        subprocess.call([python_path, os.path.join("magla", "flask", "app.py")], shell=False, env=env)
    elif target == 1:
        # start python shell
        subprocess.call([python_path], shell=False, env=env)
    elif target == 2:
        # start nuke interactive instance
        subprocess.call([config.get("nuke_{system}".format(
            system=platform.system().lower()))], shell=False, env=env)
    elif target == 3:
        # return environment dict
        return env

    return

if __name__ == "__main__":
    import sys
    import json
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group()  # this ensures only one arg can be used at a time
    grp.add_argument(
        "-s",
        "--server",
        action="store_true",
        help="Launch Flask server(./magla/flask/app.py).")
    grp.add_argument(
        "-p",
        "--python",
        action="store_true",
        help="Launch a Python 3 shell for importing and using magla module interactively.")
    grp.add_argument(
        "-n",
        "--nuke",
        action="store_true",
        help="Launch a Nuke interactive instance for importing and using magla module.")
    grp.add_argument(
        "-e",
        "--environ",
        action="store_true",
        help="Return the prepared environment dict.")
    args = parser.parse_args()
    
    # generate int representing target
    target_choice = (args.server, args.python, args.nuke, args.environ).index(True)  
    sys.stdout.write(json.dumps(main(target_choice)))