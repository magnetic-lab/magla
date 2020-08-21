# -*- coding: utf-8 -*-
"""MagLa CLI Interface"""
import argparse
import codecs
import logging
import os
import types


def recursive_call(module, call_chain, call_chain_args, verbose=True):
    """Treat the array of strings as a namespace and call the last thing in the list.

    example:
        [magla, MaglaEnvironment, get_user]
    -->
        magla.MaglaEnvironment.get_user()

    :param module: The current module or class object in the call-chain
    :type: function | Class
    :param call_chain: list of call_chain taken from the terminal
    :type: list of str
    """
    property_name = call_chain[0]
    try:
        sub_module = getattr(module, property_name)
    except AttributeError:
        print("[ERROR] '{}' does not have a '{}' property!".format(
            module.__name__, property_name))
        return False

    if len(call_chain) == 1:
        result = None

        try:
            if call_chain_args:
                result = sub_module(*call_chain_args)
            else:
                result = sub_module() if callable(sub_module) else sub_module
        except Exception as e:
            logging.error(e.message)
            if verbose:
                raise

        return result

    call_chain.pop(0)

    return recursive_call(sub_module, call_chain, call_chain_args)

if __name__ == "__main__":

    import magla

    PARSER = argparse.ArgumentParser(
        description="Magnetic-Lab Official Production API ©2019. Author: Jacob Martinez.")

    MAGLA_CALLER_HELP = """
    Treat the array of strings as a namespace and call the last thing in the list.

    example:
        [magla, MaglaEnvironment, get_user]
    -->
        magla.MaglaEnvironment.get_user()
    """
    PARSER.add_argument("magla_caller", nargs="*", help=MAGLA_CALLER_HELP)

    ARGS_HELP = "Arguments to pass to the call chain."
    PARSER.add_argument("-a", "--args", nargs="*", help=ARGS_HELP)

    CALL_CHAIN = PARSER.parse_args().caller
    CALL_CHAIN_ARGS = PARSER.parse_args().args

    RESULT = recursive_call(magla, CALL_CHAIN, CALL_CHAIN_ARGS)
    if RESULT:
        print(RESULT)
