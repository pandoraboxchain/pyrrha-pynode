from ladon.ladonizer import ladonize


class WebAPIImpl(object):
    """
    Web API implementing reading and setting worker node properties via JSON-RPC interface, exposing API spec with
    JSON-WSD. We use `ladon` package to build both (see (ladonize)[ladonize.org] for details).
    """

    @ladonize(rtype={str: object})
    def status(self):
        pass
