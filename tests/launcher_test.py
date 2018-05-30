import logging
import sys
import unittest
import os

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


def launch_moc_service(*args):
    if 'tests' in os.getcwd():
        os.chdir('../pynode')
    loader_unit = unittest.TestLoader()
    # acceptance unit launcher
    start_dir = 'unit'
    suite_unit = loader_unit.discover(start_dir)
    runner = unittest.TextTestRunner(failfast=True)
    # runner.run(suite_unit)
    ret = not runner.run(suite_unit).wasSuccessful()
    sys.exit(ret)


if __name__ == "__main__":
    launch_moc_service(sys.argv)
