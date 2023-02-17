import exception as e
import utils as u
import re


class Path:
    def __init__(self, path: str) -> None:
        self.path = u.valid_type(path, str)

        if re.match(r"^[\w/\.]+$", path):
            self.path = path
        else:
            raise e.InvalidPath("path does not match pattern")

    def get(self) -> str:
        return self.path


def valid_type(value: any, type: any) -> any:
    if isinstance(value, type):
        return value
    else:
        raise TypeError(
            f"expected {type.__name__} (received {value.__class__.__name__})")


def isiterable(element: any) -> any:
    try:
        _ = (e for e in element)
        return True
    except:
        return False


def where(fields: dict) -> str:
    where = []

    for name, value in fields.items():
        where.append(name + " = " + str(value))

    return "WHERE " + " AND ".join(where)


def values(values: list) -> str:
    values_ = []

    for value in values:
        values_.append(str(value))

    return "VALUES (" + ", ".join(values_) + ")"


def values_v2(values: dict) -> str:
    where = []

    for name, value in values.items():
        where.append(name + " = " + str(value))

    return ", ".join(where)


if __name__ in "__main__":
    pass
