
class Manager:
    """
    Manage is global singleton for setting mode variables, global triggers
    Also will be used for saving metrics for perform operative access to
    pynode current states
    """

    # launch mode values
    # 0 = SOFT mode (current soft mode without raise exception for normal node work)
    # 1 = HARD mode (strict mode with raises exception for tests, debug and development)
    launch_mode = 0

    __instance = None

    def __init__(self):
        if Manager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Manager.__instance = self

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Manager.__instance is None:
            Manager()
        return Manager.__instance

