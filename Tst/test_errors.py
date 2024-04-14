from pathlib import Path
import os
import sys

sys.path.append(os.path.join(Path(__file__).parent.parent, "src"))


from error_proxy import error_proxy
from exceptions import argument_exception, operation_exception

import unittest


class test_errors(unittest.TestCase):
    def test_check_set_error_text(self):
        # Podg"
        error = error_proxy("Test", "test")

        assert error.if_error == True

    def test_check_set_exception(self):
        # podg
        error = error_proxy()

        try:
            result = 1 / 0
        except Exception as ex:
            error.create_error(ex)

        assert error.if_error

    def test_check_argument_exception(self):
        # podg
        try:
            raise argument_exception
            assert False == True

        except Exception as ex:
            assert True == True
            return

        assert False == True

    def test_check_operation_exception(self):
        # podg
        try:
            raise operation_exception
            assert False == True

        except Exception as ex:
            assert True == True
            return

        assert False == True
