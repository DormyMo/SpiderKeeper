def project_path():
    import os
    import inspect
    this_file = inspect.getfile(inspect.currentframe())
    return os.path.abspath(os.path.dirname(this_file)+'/../')
