'Autoclose object.'

class AutoClose:
    'Autoclosing object. Calls close() on scope leave.'
    def __init__(self, closable):
        self.__closable = closable
    def __enter__(self):
        return self.__closable
    def __exit__(self, type, value, traceback):
        try:
            self.__closable.close()
        except:
            if not type:
                raise
