import sqlite3

import utils as u
import exception as e
import field as f
import table as t


class Database:
    def __init__(self, type: str, path: u.Path) -> None:
        types: list = [
            "SQLITE3"
        ]

        if isinstance(type, str):

            if type in types:
                self.type: str = type
            else:
                raise e.InvalidType(f"this type ({type}) is not allowed")

        else:
            raise TypeError("expected str (type)")

        if isinstance(path, u.Path):
            self.path: str = path.get()
        else:
            raise TypeError("expected utils.Path (path)")

        self.__connect = sqlite3.connect(path.get())
        self.__cursor = self.__connect.cursor()

    def save(self) -> None:
        self.__connect.commit()

    def addTable(self, table_class: f.TableClass, live_update=False) -> t.Table:
        return t.Table(table_class, self.__connect, self.__cursor, live_update=live_update)

    def deleteTable(self, table_class: f.TableClass) -> None:
        u.valid_type(table_class, f.TableClass)
        self.__cursor.execute(f"DROP TABLE  IF EXISTS {table_class.name}")
