from Src.Logics.process_factory import process_factory
from Src.Logics.storage_prototype import storage_prototype
from Src.exceptions import argument_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Storage.storage import storage
from Src.Models.event_type import event_type
from Src.Logics.storage_observer import storage_observer
from Src.Logics.Services.abstract_service import abstract_sevice
from Src.settings import settings
import uuid
import json
from Src.Logics.Reporting.Json_convert.reference_conventor import reference_conventor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.error_proxy import error_proxy
from Src.Models.range_model import range_model
from Src.Storage.storage_journal_row import storage_journal_row
from Src.Storage.storage_turn_model import storage_turn_model
from Src.Models.log_type_model import log_type
from Src.Models.reciepe_model import reciepe_model
from Src.Storage.storage_factory import storage_factory
from Src.Storage.storage_journal_transaction import storage_journal_transaction

from datetime import datetime


class storage_service(abstract_sevice):
    __data = []
    __options = None
    __blocked = []

    # конструктор
    def __init__(self, data: list):

        if len(data) == 0:
            raise argument_exception("Wrong argument")

        self.__data = data
        storage_observer.observers.append(self)

    @property
    def options(self):
        return self.__options

    @options.setter
    def options(self, value: settings):
        if not isinstance(value, settings):
            raise argument_exception("неверный аргумент")
        self.__options = value

    # объединить обороты
    @staticmethod
    def _colide_turns(base_turns: list, added_turns: list):
        if len(added_turns) == 0:
            return base_turns
        for index, cur_base_turn in enumerate(base_turns):

            for aded_index, cur_added_turn in enumerate(added_turns):

                if (
                    cur_base_turn.nomenclature == cur_added_turn.nomenclature
                    and cur_base_turn.storage_id == cur_added_turn.storage_id
                ):
                    base_turns[index].amount += cur_added_turn.amount
                    added_turns.pop(aded_index)
                    break

        for cur_added_turn in added_turns:
            base_turns.append(cur_added_turn)
        return base_turns

    # получить обооты за период по номенклатуре
    def create_turns_by_nomenclature(
        self, start_date: datetime, finish_date: datetime, id: uuid.UUID
    ) -> dict:

        if not isinstance(start_date, datetime) or not isinstance(
            finish_date, datetime
        ):
            raise argument_exception("Неверный аргумент")

        if start_date > finish_date:
            raise argument_exception("Неверно переданы аргументы")

        prototype = storage_prototype(self.__data)

        # фильтруем полученные после даты блокировки по номенклатуре
        transactions = prototype.filter_date(
            self.__options.block_period, finish_date
        ).data
        transactions = prototype.filter_nom_id(id)

        # фильтруем до блока
        base = storage_prototype(self.__blocked).filter_nom_id(id)

        # конвентор
        reference = reference_conventor(
            nomenclature_model,
            error_proxy,
            nomenclature_group_model,
            range_model,
            storage_journal_row,
            storage_turn_model,
        )

        proces = process_factory()

        data = proces.create(storage.process_turn_key(), transactions.data)

        data = self._colide_turns(base.data, data)

        result = {}
        for index, cur_tran in enumerate(data):
            result[index] = reference.convert(cur_tran)

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_debug(),
                "создание оборотв по номенклатуре ",
                "storage_service.py/create_turns_by_nomenclature",
            )
        )

        return result

    # получить обооты за период
    def create_turns(self, start_date: datetime, finish_date: datetime) -> dict:

        if not isinstance(start_date, datetime) or not isinstance(
            finish_date, datetime
        ):
            raise argument_exception("Неверный аргумент")

        if start_date > finish_date:
            raise argument_exception("Неверно переданы аргументы")

        prototype = storage_prototype(self.__data)

        # фильтруем полученные после даты блокировки
        transactions = prototype.filter_date(self.__options.block_period, finish_date)

        # конвентор
        reference = reference_conventor(
            nomenclature_model,
            error_proxy,
            nomenclature_group_model,
            range_model,
            storage_journal_row,
            storage_turn_model,
        )

        proces = process_factory()

        data = proces.create(storage.process_turn_key(), transactions.data)

        data = self._colide_turns(self.__blocked, data)
        print(self.__blocked)
        result = {}
        for index, cur_tran in enumerate(data):
            result[index] = reference.convert(cur_tran)

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_debug(),
                "создание оборотoв",
                "storage_service.py/create_turns",
            )
        )
        return result

    # получить обороты по номенклатуре
    def create_id_turns(self, id: uuid.UUID):
        if not isinstance(id, uuid.UUID):
            raise argument_exception("Неверный аргумент")

        prototype = storage_prototype(self.__data)

        # фильтруем
        transactions = prototype.filter_nom_id(id)

        # конвентор
        reference = reference_conventor(
            nomenclature_model,
            error_proxy,
            nomenclature_group_model,
            range_model,
            storage_journal_row,
            storage_turn_model,
        )

        proces = process_factory()

        data = proces.create(storage.process_turn_key(), transactions.data)

        result = {}
        for index, cur_tran in enumerate(data):
            result[index] = reference.convert(cur_tran)

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_debug(),
                "получить обороты по номенклатуре",
                "storage_service.py/create_id_turns",
            )
        )

        return result

    # создать транзакции по рецепту
    def create_reciepe_transactions(self, reciepe: reciepe_model):
        if not isinstance(reciepe, reciepe_model):
            raise argument_exception("Неверный аргумент")

        prototype = storage_prototype(self.__data)

        # фильтруем
        transactions = prototype.filter_reciepe(reciepe)

        # оборот
        proces = process_factory()
        turn = proces.create(storage.process_turn_key(), transactions.data)

        transactions_list = []
        # пробегаемся по обороту
        for cur_ing in list(reciepe.ingridient_proportions.keys()):
            # флаг для проверки на присутствие на складах
            flag = True
            for cur_nom in turn:
                if cur_ing.id == cur_nom.nomenclature.id:
                    amount = list(reciepe.ingridient_proportions[cur_ing].keys())[0]

                    # пересчитываем единицы измерения
                    if cur_ing.ran_mod != cur_nom.nomenclature.ran_mod:
                        amount *= cur_ing.ran_mod.recount_ratio

                    transactions_list.append(
                        storage_factory.create_transaction(
                            False, cur_ing, amount, datetime.now()
                        )
                    )
                    flag = False
                    break

            # если в обороте не найдена номенклатура кидаем not found
            if not flag:
                transactions_list.append(f"{cur_nom.nomenclature.id} not found")

        reference = reference_conventor(
            nomenclature_model,
            error_proxy,
            nomenclature_group_model,
            range_model,
            storage_journal_row,
            storage_turn_model,
            storage_journal_transaction,
        )
        result = {}
        for index, cur_tran in enumerate(transactions_list):

            # так как reference conventor работает только со сложными типами данных, делаем разделение
            if isinstance(cur_tran, str):
                result[index] = cur_tran
                continue

            result[index] = reference.convert(cur_tran)

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_debug(),
                "создать транзакции по рецепту",
                "storage_service.py/create_reciepe_transactions",
            )
        )

        return result

    # рейтинг номенклатуры по складам и айди
    def create_id_turns_storage(self, nomenclature_id: uuid.UUID, storage_id: str):
        if not isinstance(nomenclature_id, uuid.UUID):
            raise argument_exception("Неверный аргумент")

        transactions = storage_prototype(self.__data)

        if storage_id is not None:
            transactions = transactions.filter_storage(uuid.UUID(storage_id))

        # фильтруем
        transactions = transactions.filter_nom_id(nomenclature_id)

        # конвентор
        reference = reference_conventor(
            nomenclature_model,
            error_proxy,
            nomenclature_group_model,
            range_model,
            storage_journal_row,
            storage_turn_model,
        )

        proces = process_factory()

        data = proces.create(storage.process_turn_key(), transactions.data)

        data_turn_sort = {}

        # по ключам оборота делаем слвоарь складов
        for cur_turn in data:
            data_turn_sort[cur_turn.amount] = cur_turn

        keys = list(data_turn_sort.keys())

        keys.sort(reverse=True)

        result = {}
        for index, cur_tran in enumerate(keys):
            result[index] = reference.convert(data_turn_sort[cur_tran])

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_debug(),
                "рейтинг номенклатуры по складам и айди",
                "storage_service.py/create_id_turns_storage",
            )
        )
        return result

    # получить обооты до периода блокировки
    def create_blocked_turns(self) -> dict:

        prototype = storage_prototype(storage().data[storage.journal_key()])

        # фильтруем
        transactions = prototype.filter_date(
            datetime(1999, 1, 1), self.__options.block_period
        )

        proces = process_factory()

        data = proces.create(storage.process_turn_key(), transactions.data)

        # сохраняем обороты в сервис
        storage().data[storage.b_turn_key()] = data
        self.__blocked = data
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_debug(),
                "получить обооты до периода блокировки",
                "storage_service.py/create_blocked_turns",
            )
        )
        return data

    def handle_event(self, handle_type: str):
        super().handle_event(handle_type)

        if handle_type == event_type.changed_block_period():
            self.create_blocked_turns()

    @staticmethod
    def create_response(data: dict, app):

        if app is None:
            raise argument_exception()
        json_text = json.dumps(data)

        # Подготовить ответ
        result = app.response_class(
            response=f"{json_text}",
            status=200,
            mimetype="application/json; charset=utf-8",
        )

        return result
