
def run_once(method):
    """A decorator that runs a method only once."""

    attrname = "_%s_once_result" % id(method)

    def decorated(self, *args, **kwargs):
        try:
            return getattr(self, attrname)
        except AttributeError:
            setattr(self, attrname, method(self, *args, **kwargs))
            return getattr(self, attrname)
    return decorated
