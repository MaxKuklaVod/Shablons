from pathlib import Path
import os
import sys

sys.path.append(os.path.join(Path(__file__).parent.parent, "src"))

from datetime import datetime
from Src.Storage.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Storage.storage_factory import storage_factory
from Src.Models.range_model import range_model


import unittest


class test_storage(unittest.TestCase):

    # создать склад
    def test_check_storage_model(self):
        # подготовка
        loc = "    Улица малых богов 123       "

        # действие
        item = storage_model(loc)

        # проверка
        print(item.id)
        assert item.location == "Улица малых богов 123"
        assert item.id is not None

    # создать действие на складе
    def test_check_journal_transaction(self):
        # подготовка
        nom = nomenclature_model()

        # действие
        item = storage_factory.create_transaction(True, nom, 23, datetime.now())
        print(item.amount)

        # проверка
        assert item.amount == 23
        assert item.id is not None
        assert item.type == "add"
        assert item.period.month == datetime.now().month

    # создать журнальную строку
    def test_build_journal_row(self):
        # подготовка
        nom = nomenclature_model()
        item1 = storage_factory.create_transaction(True, nom, 2, datetime(2014, 12, 1))
        loc = "    Улица малых богов 123       "
        item2 = storage_model(loc)

        # действие
        item3 = storage_factory.create_row(item2, item1)

        # проверка
        assert item3.amount == item1.amount
        assert item3.location == item2.location
        assert item3.operation_id == item1.id
        assert item3.storage_id == item2.id
        assert item3.period == item1.period
        assert item3.operation_type == item1.type

    # создать
    def test_build_turn_model(self):
        # подготовка
        nom = nomenclature_model()
        item1 = storage_factory.create_transaction(True, nom, 2, datetime(2014, 12, 1))
        loc = "    Улица малых богов 123       "
        item2 = storage_model(loc)
        ran = range_model()
        nom = nomenclature_model()

        # действие
        item3 = storage_factory.create_row(item2, item1)

        # действие
        item = storage_factory.create_turn(item3.storage_id, 23, nom, ran)

        # проверка
        assert item.amount == 23
        assert item.range == ran
        assert item.nomenclature == nom
        assert item.storage_id == item3.storage_id
