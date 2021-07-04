import argparse
from pprint import pformat
import sys

import magla


class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value

if __name__ == "__main__":
    r = magla.Root()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    parser_create = subparsers.add_parser(
        "create",
        help="create entity from data",
    )
    parser_create.set_defaults(callback=r.create)
    parser_create.add_argument("entity", type=str)
    parser_create.add_argument("config", nargs="*", action=ParseKwargs)
    
    parser_create_from_config = subparsers.add_parser(
        "create_from_config",
        help="create entities from `yaml` config file"
    )
    parser_create_from_config.set_defaults(callback=r.create_from_config)
    parser_create_from_config.add_argument("config_path", type=str)
    
    parser_version_up = subparsers.add_parser(
        "version_up",
        help="create new version for given shot id"
    )
    parser_version_up.set_defaults(callback=r.version_up)
    parser_version_up.add_argument("shot_id", type=int)
    
    parser_all = subparsers.add_parser(
        "all",
        help="retrieve list of all entities currently in the database"
    )
    parser_all.set_defaults(callback=r.all)
    
    parser_all = subparsers.add_parser(
        "get",
        help="retrieve list of all entities of given type"
    )
    parser_all.set_defaults(callback=r.all)
    parser_all.add_argument("entity", type=str)
    # NOTE: Python 2 will error 'too few arguments' if no subcommand is supplied.
    #       No such error occurs in Python 3, which makes it feasible to check
    #       whether a subcommand was provided (displaying a help message if not).
    #       argparse internals vary significantly over the major versions, so it's
    #       much easier to just override the args passed to it.
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    
    args = parser.parse_args()
    if args.callback == r.create:
        args.callback(magla.Entity.type(args.entity), args.config)
    elif args.callback == r.create_from_config:
        args.callback(args.config_path)
    elif args.callback == r.version_up:
        args.callback(args.shot_id)
    elif args.callback == r.all:
        if args.entity:
            result = args.callback(magla.Entity.type(args.entity))
        else:
            result = args.callback()
        sys.stdout.write(pformat(result))
        sys.stdout.write("\n")