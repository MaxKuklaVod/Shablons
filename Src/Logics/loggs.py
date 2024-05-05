from Src.error_proxy import error_proxy
from Src.Storage.storage import storage
from Src.Logics.storage_observer import storage_observer
from Src.Models.event_type import event_type
from Src.Logics.Reporting.Json_convert.reference_conventor import reference_conventor
from pathlib import Path
import json


class loggs:
    __storage = None
    __log = None
    __save_path = "/Src/Storage/Saved_models/logs.json"

    def __init__(self) -> None:
        self.__storage = storage()
        storage_observer.observers.append(self)

    def handle_event(self, event: str):
        splitted = event.split(" ")
        if splitted[0] == event_type.make_log_key():
            self._create_log(splitted[1], splitted[2], splitted[3])
            self._save_log()

    def _create_log(self, type: str, text: str, source: str):
        self.__log = error_proxy(text, source)
        self.__log.log_type = type
        print(list(self.__storage.data.keys()))
        self.__storage.data[storage.logs_key()].append(self.__log)

    def _save_log(self):
        ref = reference_conventor(error_proxy)
        ret = ref.convert(self.__log)
        get = None
        to_write = json.dumps(ret, ensure_ascii=False)
        
        with open(self.__save_path, "r+") as saved_json:
            if self.__save_path.stat().st_size == 0:
                saved_json.write(json.dumps({"logs": [to_write]}))
            else:
                get = json.load(saved_json)
                get["logs"].append(to_write)

        if get is not None:
            with open(self.__save_path, "w") as saved_json:
                saved_json.write(json.dumps(get, ensure_ascii=False))
