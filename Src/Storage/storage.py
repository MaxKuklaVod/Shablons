class storage:
    __data = {}

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage, cls).__new__(cls)
        return cls.instance

    @property
    def data(self):
        return self.__data

    @staticmethod
    def nomenclature_key():
        return "nomenclature"

    @staticmethod
    def group_key():
        return "group"

    @staticmethod
    def unit_key():
        return "unit"

    @staticmethod
    def reciepe_key():
        return "reciepe"

    @staticmethod
    def journal_key():
        return "journal"

    @staticmethod
    def process_turn_key():
        return "process_turn"

    @staticmethod
    def turn_key():
        return "block_turn"
