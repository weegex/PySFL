import utils as u
import exception as e
import field as f
import sqlite3
import re


class TableObject:
    def __init__(self, fields: dict, table, connect: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
        self.__table = table
        self.__fields = fields
        self.__old_fields = fields
        self.__table_fields = table.fields
        self.__connect = connect
        self.__cursor = cursor

        for name, value in fields.items():
            self.__dict__[name] = value

    @property
    def fields(self) -> dict:
        return self.__fields

    @property
    def old_fields(self) -> dict:
        return self.__old_fields

    def delete(self) -> bool:
        return self.__table.delete(**self.__fields)

    def __setattr__(self, name, value) -> None:
        try:
            if name in self.__fields:
                self.__old_fields = self.__fields.copy()
                self.__fields[name] = value

                if self.__table.live_update:
                    self.save()
        except AttributeError as e:
            pass

        self.__dict__[name] = value

        return value

    def save(self) -> bool:
        old_dict = {}
        dict = {}

        for field, value in self.__old_fields.items():
            if field in self.__table_fields:
                old_dict[field] = self.__table_fields[field].setValue(value)
            else:
                raise KeyError(f"non-existent field name {field}")

        for field, value in self.__fields.items():
            if field in self.__table_fields:
                if self.__old_fields[field] != self.__fields[field]:
                    dict[field] = self.__table_fields[field].setValue(value)
            else:
                raise KeyError(f"non-existent field name {field}")

        where = u.values_v2(dict)
        old_where = u.where(old_dict)

        if not where:
            return True

        self.__cursor.execute(
            f"UPDATE {self.__table.name} SET {where} {old_where}")

        if not self.__table.exists(**self.__fields):
            raise e.UpdateFailed(
                f"failed to update object ({self.__table.name})")
        else:
            return True


class Table:
    def __init__(self, table_class: f.TableClass, connect: sqlite3.Connection, cursor: sqlite3.Cursor, live_update=False) -> None:
        self.__table_class: f.TableClass = u.valid_type(
            table_class(), f.TableClass)
        self.__name: str = self.__table_class.__class__.__name__.lower()
        self.__fields = self.__table_class.__dict__
        self.__live_update = live_update

        self.__connect: sqlite3.Connection = u.valid_type(
            connect, sqlite3.Connection)
        self.__cursor: sqlite3.Cursor = u.valid_type(cursor, sqlite3.Cursor)

        created = False

        try:
            self.__cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.name} ({self.__convertFieldsToString()})"
            )
            created = True
        except sqlite3.OperationalError:
            created = False

        if not created:
            raise e.CreateTableError(f"table already exists ({self.__name})")

        self.__connect.commit()

    @property
    def fields(self) -> dict:
        return self.__fields

    @property
    def name(self) -> str:
        return self.__name

    @property
    def live_update(self) -> bool:
        return self.__live_update

    def __convertFieldsToString(self) -> str:
        fieldsString = []
        primary = False

        for name, value in self.__fields.items():
            if value.is_primaryKey() and primary:
                raise e.PrimaryKeyError(f"primary key already set ({name})")
            elif value.is_primaryKey() and not primary:
                primary = True

            fieldsString.append(name + " " +
                                value.type + " " + value.additionals)
        return ", ".join(fieldsString)

    def __convertFieldsToStringQuery(self, dict) -> tuple:
        names = []
        values = []

        for name, value in dict.items():
            names.append(str(name))
            values.append(str(value))

        return ", ".join(names), ", ".join(values)

    def get(self, **fields) -> TableObject:
        dict = {}

        for field, value in fields.items():
            if field in self.__fields:
                dict[field] = self.__fields[field].setValue(value)
            else:
                raise KeyError(f"non-existent field name {field}")

        where = u.where(dict)

        self.__cursor.execute(f"SELECT * FROM {self.name} {where}")
        object = self.__cursor.fetchone()

        if object:
            dict = {}
            i = 0

            for name in self.__fields:
                dict[name] = object[i]
                i += 1

            object = type("SQLObject_" + self.name,
                          (TableObject,), {})

            return object(dict, self, self.__connect, self.__cursor)
        else:
            raise e.GetFailed(f"failed to get object ({self.name})")

    def exists(self, *args, **fields) -> TableObject:
        try:
            self.get(**fields)
            return True
        except e.GetFailed:
            return False

    def add(self, **fields) -> TableObject:
        dict = {}
        for name, value in self.__fields.items():
            try:
                dict[name] = value.setValue(fields[name])
            except KeyError:
                if not value.null:
                    raise ValueError(f"{self.name} field cannot be empty")

        names = []

        for name in dict:
            names.append(name)

        names = ", ".join(names)
        values = u.values(dict.values())

        created = False

        try:
            self.__cursor.execute(
                f"INSERT INTO {self.name} ({names}) {values}")
            created = True
        except sqlite3.IntegrityError:
            created = False

        if created:
            try:
                result = self.get(**fields)
                return result
            except e.GetFailed:
                pass

        raise e.AddFailed(f"failed to add object ({self.name})")

    def delete(self, **fields) -> bool:
        dict = {}

        for field, value in fields.items():
            if field in self.__fields:
                if not value is None:
                    dict[field] = self.__fields[field].setValue(value)
            else:
                raise KeyError(f"non-existent field name {field}")

        where = u.where(dict)

        self.__cursor.execute(f"DELETE FROM {self.name} {where}")

        if self.exists(**fields):
            return False
        else:
            return True
