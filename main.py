from flask import Flask, request
from Src.settings_manager import settings_manager
from Src.Storage.storage import storage
from Src.errors import error_proxy
from Src.Logics.report_factory import report_factory
from Src.Logics.start_factory import start_factory
from datetime import datetime
from Src.Logics.storage_service import storage_service
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(Path(__file__).parent, "src"))


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# Сформировать начальный набор данных
options = settings_manager()
start = start_factory(options.settings)
start.create()

set = settings_manager()
add = os.path.join(Path(__file__).parent, "Jsons")
set.open("Src/settings.json", add)
item = start_factory(set.settings)
item.create()


@app.route("/api/report/<storage_key>", methods=["GET"])
def get_report(storage_key: str):
    """
        Сформировать отчет
    Args:
        storage_key (str): Ключ - тип данных: номенклатура, группы и т.д.
    """

    keys = storage.storage_keys(start.storage)
    if storage_key == "" or storage_key not in keys:
        return error_proxy.create_error_response(
            app,
            f"Некорректный передан запрос! Необходимо передать: /api/report/<storage_key>. Список ключей (storage_key): {keys}.",
            400,
        )

    # Создаем фабрику
    report = report_factory()
    data = start.storage.data

    # Формируем результат
    try:
        result = report.create_response(
            options.settings.report_mode, data, storage_key, app
        )
        return result
    except Exception as ex:
        return error_proxy.create_error_response(
            app, f"Ошибка при формировании отчета {ex}", 500
        )


@app.route("/api/storage/turns", methods=["GET"])
def get_turns():
    # Получить параметры
    args = request.args
    if "start_period" not in args.keys():
        return error_proxy.create_error_response(
            "Необходимо передать параметры: start_period, stop_period!"
        )

    if "stop_period" not in args.keys():
        return error_proxy.create_error_response(
            "Необходимо передать параметры: start_period, stop_period!"
        )

    start_date = datetime.strptime(args["start_period"], "%Y-%m-%d")
    stop_date = datetime.strptime(args["stop_period"], "%Y-%m-%d")

    source_data = start.storage.data[storage.storage_transaction_key()]
    data = storage_service(source_data).create_turns(start_date, stop_date)
    result = storage_service.create_response(data, app)
    return result


@app.route("/api/settings/mode/period", methods=["GET"])
def change_block_period():
    args = request.args

    if "block_period" not in args.keys():
        response = storage_service.create_response(
            {"block_period": str(set.settings.block_period)}, app
        )
        return response
    set.settings.block_period = args["block_period"]
    set.save_settings()
    response = storage_service.create_response(
        {"block_period": str(set.settings.block_period)}, app
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)
