

def startup(config=None):
    """Import each python file detected in module_LOCATION.

    :param config: <dict> containing info from config.txt.
    """
    startup = __import__(Path.resolve("<touchdesigner_python_startup>"))
    # sys.path.append(startup_scripts_dir)

    # returns = []
    # for path_to_py_file in _get_py_files(startup_scripts_dir):

    #     py_file = os.path.splitext(path_to_py_file)[0]
    #     module = importlib.import_module(py_file.replace("\\", "/"))

    #     # append whatever the module startup returns, if anything
    #     returns.append(module.startup())

    # sys.path.remove(startup_scripts_dir)

    return startup.main()
