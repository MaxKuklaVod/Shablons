from flask import Flask, send_file, request
import uuid
from Src.settings_manager import settings_manager
from Src.Storage.storage import storage
from Src.errors import error_proxy
from Src.Logics.report_factory import report_factory
from Src.Logics.start_factory import start_factory
from datetime import datetime
from Src.Logics.Services.storage_service import storage_service
from Src.Models.nomenclature_model import nomenclature_model
from Src.Logics.storage_observer import storage_observer
from Src.Models.event_type import event_type
from Src.Models.log_type_model import log_type
from Src.Logics.Services.nomenclature_service import nomenclature_service


app = Flask(__name__)

unit = settings_manager()
item = start_factory(unit.settings)
item.create()


# по ссылке выдаёт результат
@app.route("/api/report/<storage_key>", methods=["GET"])
def get_report(storage_key: str):

    check = [
        storage.unit_key(),
        storage.group_key(),
        storage.reciepe_key(),
        storage.nomenclature_key(),
        storage.journal_key(),
    ]

    # preparation

    factory = report_factory()

    result = storage_key

    report_type = item.options.report_type
    # action

    if storage_key in check:

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"Получить репорт {storage_key}",
                "main.py/get_report",
            )
        )
        result = factory.create(report_type, item.storage.data, storage_key)
        return send_file(f"report.{report_type.lower()}")

    else:
        text = "Ошибка ввода ключа"
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"{text}", "main.py/get_report"
            )
        )
        return error_proxy.create_response(app, text, 404)


@app.route("/api/storage/<nomenclature_id>/turns", methods=["GET"])
def get_nomenclature_rests(nomenclature_id: uuid.UUID):
    key = storage.journal_key()

    # генерация работает, однако столкнулся с проблемой - тк айди каждый раз генериться случайно, узнать актуальный айди для фильтрации - можно  только из других запросов
    try:

        data = storage_service(item.storage.data[key]).create_id_turns(
            uuid.UUID(nomenclature_id)
        )
    except:
        text = "Ошибка ввода айди"
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"{text}", "main.py/get_nomenclature_turns"
            )
        )
        return error_proxy.create_response(app, text, 500)

    storage_observer.raise_event(
        event_type.make_log(
            log_type.log_type_info(),
            f"Получить оборот по  {nomenclature_id}",
            "main.py/get_nomenclature_turns",
        )
    )

    responce_type = storage_service.create_response(data, app)

    return responce_type


@app.route("/api/storage/rests", methods=["GET"])
def get_rests():

    key = storage.journal_key()

    args = request.args
    if ("start_period") not in args.keys():
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка ввода ключа", "main.py/get_rests"
            )
        )
        return error_proxy.create_response(app, "Ошибка ввода ключа", 404)
    if ("stop_period") not in args.keys():
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка ввода ключа", "main.py/get_rests"
            )
        )
        return error_proxy.create_response(app, "Ошибка ввода ключа", 404)

    start_date = datetime.strptime(args["start_period"], "%Y-%m-%d")
    finish_date = datetime.strptime(args["stop_period"], "%Y-%m-%d")

    serv = storage_service(item.storage.data[key])
    serv.options = unit.settings
    data = serv.create_turns(start_date, finish_date)

    response_type = storage_service.create_response(data, app)

    storage_observer.raise_event(
        event_type.make_log(
            log_type.log_type_info(), f"Получить складские остатки", "main.py/get_rests"
        )
    )

    return response_type


@app.route("/api/storage/<receipt_id>/debits", methods=["GET"])
def get_debits(receipt_id: str):
    text = "not_found"

    # на случай если указанного айди не существует
    response_type = app.response_class(
        response=f"{text}", status=404, mimetype="application/text"
    )

    # генерация работает, однако столкнулся с проблемой - тк айди каждый раз генериться случайно, узнать актуальный айди для фильтрации - можно  только из других запросов
    try:
        id = uuid.UUID(receipt_id)
    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/get_debits"
            )
        )
        return response_type

    journal = storage.journal_key()
    rec = storage.reciepe_key()

    # ищем рецепт по айди
    for cur_reciepe in item.storage.data[rec]:
        print(id, cur_reciepe.id)
        # если нашли совпадение - начинаем работу
        if id == cur_reciepe.id:
            data = storage_service(
                item.storage.data[journal]
            ).create_reciepe_transactions(cur_reciepe)
            response_type = storage_service.create_response(data, app)
            break

    storage_observer.raise_event(
        event_type.make_log(
            log_type.log_type_info(),
            f"Создать транзакции по рецепту",
            "main.py/get_debits",
        )
    )
    return response_type


@app.route("/api/storage/<nomenclature_id>/rests", methods=["GET"])
def get_sorted_turn(nomenclature_id: str):

    args = request.args
    storage_id = None

    key = storage.journal_key()
    if "storage_id" in args.keys():
        storage_id = args["storage_id"]

    try:
        # генерация работает, однако столкнулся с проблемой - тк айди каждый раз генериться случайно, узнать актуальный айди для фильтрации - можно  только из других запросов
        data = storage_service(item.storage.data[key]).create_id_turns_storage(
            uuid.UUID(nomenclature_id), storage_id
        )
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"обороты номенклатуры по рейтингу с id {storage_id}",
                "main.py/get_sorted_turn",
            )
        )
    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/get_sorted_turn"
            )
        )
        return error_proxy.create_response(app, "Ошибка ввода айди", 404)

    responce_type = storage_service.create_response(data, app)

    return responce_type


# изменение is_first_start
@app.route("/api/settings/mode/<mode_type>", methods=["GET"])
def switch_mode(mode_type):
    try:

        unit.settings.is_first_start = mode_type
        unit.save_settings()

        response = storage_service.create_response(
            {"is_first_start": str(str(mode_type).lower() == "true")}, app
        )
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"изменить is_first_start на {mode_type}",
                "main.py/switch_mode",
            )
        )
        return response

    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/switch_mode"
            )
        )
        return error_proxy.create_response(app, "wrong argument", 500)


# в запросе block_period
@app.route("/api/settings/mode/period", methods=["GET"])
def change_block_period():
    args = request.args

    if "block_period" not in args.keys():
        response = storage_service.create_response(
            {"block_period": str(unit.settings.block_period)}, app
        )
        return response

    try:
        unit.settings.block_period = args["block_period"]
        unit.save_settings()
        response = storage_service.create_response(
            {"block_period": str(unit.settings.block_period)}, app
        )
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"изменить block_period",
                "main.py/change_block_period",
            )
        )
        return response
    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/change_block_period"
            )
        )
        return error_proxy.create_response(app, "ошибка", 500)


# добавление
@app.route("/api/nomenclature/add", methods=["PUT"])
def add_nomenclature():
    args = request.get_json()
    if args is None:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(),
                f"не передан аргумент",
                "main.py/add_nomenclature",
            )
        )
        return error_proxy.create_response(app, "Не передан аргумент", 404)

    try:
        # При неполном заполнении номенклатуры (нет айди и тд.) метод _load выдает Exception (сеттеры и ошибка ключа)
        nom = nomenclature_model._load(args)
        serv = nomenclature_service(item.storage.data[storage.nomenclature_key()])
        added = serv.add_nom(nom)
        item.storage.data[storage.nomenclature_key()] = added

        item.save()
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"добавить номенклатуру с id {nom.id}",
                "main.py/add_nomenclature",
            )
        )
        return nomenclature_service.create_response(args, app)

    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/add_nomenclature"
            )
        )
        # если _load выдаёт Exception, мы возвращаем "Ошибка обработки"
        return error_proxy.create_response(app, "Ошибка обработки", 500)


@app.route("/api/nomenclature/change", methods=["PATCH"])
def change_nomenclature():
    args = request.get_json()

    if args is None:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(),
                f"не передан аргумент",
                "main.py/change_nomenclature",
            )
        )
        return error_proxy.create_response(app, "Не передан аргумент", 404)

    try:
        # метод load выдаёт ошибку если какой-то из аргументов не передан
        nom = nomenclature_model._load(args)
        serv = nomenclature_service(item.storage.data[storage.nomenclature_key()])
        added = serv.change_nome(nom)
        item.storage.data[storage.nomenclature_key()] = added

        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"изменить номенклатуру с id {nom.id}",
                "main.py/change_nomenclature",
            )
        )
        item.save()
        return nomenclature_service.create_response(args, app)

    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/change_nomenclature"
            )
        )
        # ошибка обработки при неполной передачи данных
        return error_proxy.create_response(app, "Ошибка обработки", 500)


# удаление
@app.route("/api/nomenclature/delete", methods=["DELETE"])
def delete_nomenclature():
    args = request.args
    try:
        if "id" not in args.keys():
            storage_observer.raise_event(
                event_type.make_log(
                    log_type.log_type_error(),
                    f"не передан аргумент",
                    "main.py/delete_nomenclature",
                )
            )
            return error_proxy.create_response(app, "не найден аргумент", 404)

        nom_id = args["id"]
        serv = nomenclature_service(item.storage.data[storage.nomenclature_key()])

        # в сервисе получаем массив без удаляемой номенклатуры
        added, result = serv.delete_nom(nom_id)

        # сохраняем его в storage по ключу если удалили
        if result:
            item.storage.data[storage.nomenclature_key()] = added

            # сохраняем
            item.save()
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"удалить номенклатуру с id {nom_id}",
                "main.py/delete_nomenclature",
            )
        )
        return nomenclature_service.create_response({"result": result}, app)

    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/delete_nomenclature"
            )
        )
        return error_proxy.create_response(app, "Ошибка обработки", 500)


# получение (если нет айди - даёт всё)
@app.route("/api/nomenclature/get", methods=["GET"])
def get_nomenclature():
    args = request.args
    try:
        # Если в апи запросе не указан айди конкретной номенклатуры, то мы передаем все существующие номенклатуры (Конвертация происходит фабричным методом )
        if "id" not in args.keys():
            factory = report_factory()
            result = factory.create(
                "Json", item.storage.data, storage.nomenclature_key()
            )
            storage_observer.raise_event(
                event_type.make_log(
                    log_type.log_type_info(),
                    f"получить номенклатуру",
                    "main.py/get_nomenclature",
                )
            )
            return nomenclature_service.create_response(result, app)

        # иначе ищем номенклатуру по нужному нам id и возвращаем её в формате json
        nom_id = args["id"]
        serv = nomenclature_service(item.storage.data[storage.nomenclature_key()])
        added = serv.get_nom(nom_id)
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_info(),
                f"получить номенклатуру с id {nom_id}",
                "main.py/get_nomenclature",
            )
        )
        return nomenclature_service.create_response(added, app)

    except Exception as ex:
        storage_observer.raise_event(
            event_type.make_log(
                log_type.log_type_error(), f"Ошибка {ex}", "main.py/get_nomenclature"
            )
        )
        return error_proxy.create_response(app, "Ошибка обработки", 500)


if __name__ == "__main__":
    app.run(debug=True)
