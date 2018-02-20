import unittest

from test.test_manager import TestManager

# for launch test NOT from console
# place path to config file to TestManager as '../../../pynode.ini' TestManager('../../../pynode.ini')
# and to pynode launcher self.manager.run_test_pynode('../../../pynode.ini')


class TestWorkerInitialStateIDLE(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.manager = TestManager()
        cls.manager.get_configuration().set_default_values()
        cls.manager.get_configuration().worker_state = 2
        cls.manager.run_test_listener(demon=True)

    def test_initial_worker_state_idle(self):
        print('======================================================================== test_initial_worker_state_idle')
        # launch pynode
        result = self.manager.run_test_pynode()
        self.assertTrue(result, 1)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


