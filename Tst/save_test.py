from Src.settings_manager import settings_manager
from pathlib import Path
import os
import sys

sys.path.append(os.path.join(Path(__file__).parent.parent, "src"))

from Src.settings_manager import settings_manager

import unittest


class save_test(unittest.TestCase):

    def test_check_convert_json_settings(self):
        # подготовка
        manager = settings_manager()
        # адрес
        address = os.path.join(Path(__file__).parent.parent, "Jsons")
        result = manager.open("Tester.json", address)
        # действие
        try:
            dic = manager.save_settings()
            assert True == True
            return
        except:
            assert False == True
