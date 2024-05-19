import unittest
from pathlib import Path
import os
import sys

sys.path.append(os.path.join(Path(__file__).parent.parent, "src"))

from Src.Logics.start_factory import start_factory
from Src.settings_manager import settings_manager
from Src.Storage.storage import storage
from Src.Logics.Services.nomenclature_service import nomenclature_service


class observer_test(unittest.TestCase):

    def test_check_delete_nom_observer(self):
        #Подготовка
        unit=settings_manager()
        address=os.path.join(Path(__file__).parent.parent,'Jsons')
        unit.open('./Src/settings.json',address)
        unit.settings.block_period="2024-1-1"
        factory=start_factory(unit.settings)
        factory.create()

        key=storage.nomenclature_key()
        sevice=nomenclature_service(factory.storage.data[key])

        controll_rec=list(factory.storage.data[storage.reciepe_key()][0])
        controll_journal=factory.storage.data[storage.journal_key()]
        controll_blocked=factory.storage.data[storage.process_turn_key()]

        #дейсвтие  
        print(factory.storage.data[key][0].name,factory.storage.data[key][0].id)
        factory.storage.data[key],res=sevice.delete_nom(str(factory.storage.data[key][0].id))



        #проверка
        print(res)
        print(controll_rec,list(factory.storage.data[storage.reciepe_key()][0]))


        #проверка
        assert controll_rec!=list(factory.storage.data[storage.reciepe_key()][0])
        assert controll_journal!=factory.storage.data[storage.journal_key()]
        assert controll_blocked!=factory.storage.data[storage.process_turn_key()]