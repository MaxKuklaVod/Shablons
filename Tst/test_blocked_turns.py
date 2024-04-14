from pathlib import Path
import os
import sys

sys.path.append(os.path.join(Path(__file__).parent.parent, "src"))

from settings_manager import settings_manager
from datetime import datetime
from Src.Storage.storage import storage
from Src.Logics.start_factory import start_factory
from Src.Logics.storage_sevice import storage_service
import unittest


class test_blocked_turns(unittest.TestCase):

   def test_check_get_block_turns(self):
        #Подготовка
        unit=settings_manager()
        address=os.path.join(Path(__file__).parent.parent,'Jsons')
        unit.open('./Src/setting.json',address)
        factory=start_factory(unit.settings)
        factory.create()

        key=storage.journal_key()
        sevice=storage_service(factory.storage.data[key])
        sevice.options=unit.settings

        #дейсвтие  
        res=sevice.create_blocked_turns()

        #проверка
        assert res is not None
        assert len(res)>0
        assert res[0].storage_id==factory.storage.data[storage.turn_key()][0].storage_id
