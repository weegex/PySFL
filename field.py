import utils as u
import re


class Field:
    def __init__(self, null: bool = True, primary_key: bool = False, auto: bool = False) -> None:
        self.__primary_key = u.valid_type(primary_key, bool)
        self.__null = u.valid_type(null, bool)
        if self.__primary_key:
            self.__null = False
        self.__auto = u.valid_type(auto, bool)
        self.__value = None
        self.__type = None

    @property
    def additionals(self) -> str:
        additionals = []

        if self.__primary_key:
            additionals.append("PRIMARY KEY")

        if self.__null:
            additionals.append("NULL")
        else:
            additionals.append("NOT NULL")

        if self.__auto:
            additionals.append("AUTOINCREMENT")

        return " ".join(additionals)

    def is_primaryKey(self) -> bool:
        return self.__primary_key

    @property
    def auto(self) -> bool:
        return self.__auto

    @property
    def null(self) -> bool:
        return self.__null

    def validate(self, value: any) -> any:
        return value

    def get(self) -> str:
        return str(self.__value)

    @property
    def value(self) -> any:
        return self.__value

    def setValue(self, value) -> any:
        self.__value = self.validate(value)
        return self.get()

    @property
    def type(self) -> None:
        return self.__type


class TextField(Field):
    def __init__(self, null: bool = True, primary_key: bool = False) -> None:
        super().__init__(null, primary_key, False)

    def validate(self, value: any) -> any:
        if not self.null:
            return u.valid_type(value, str)
        else:
            if value is None or u.valid_type(value, str):
                return value

    def get(self) -> str:
        value = self.validate(self.value)
        if not value is None:
            if '"' in value:
                return "'" + value + "'"
            elif "'" in value:
                return '"' + value + '"'
        else:
            return "NULL"

    @property
    def type(self) -> str:
        return "TEXT"


class IntegerField(Field):
    def __init__(self, null: bool = True, primary_key: bool = False, auto: bool = False) -> None:
        super().__init__(null, primary_key, auto)

    def validate(self, value: any) -> int:
        if not self.null:
            return u.valid_type(value, int)
        else:
            if value is None or u.valid_type(value, int):
                return value

    def get(self) -> str:
        value = self.validate(self.value)
        if not value is None:
            return str(value)
        else:
            return "NULL"

    @property
    def type(self) -> str:
        return "INTEGER"


class TableClass:
    def __init__(self) -> None:
        self.__dict__ = {
            name: value

            for name, value in self.__class__.__dict__.items()
            if not re.match(r"__.+__", name) and u.valid_type(value, Field)
        }
