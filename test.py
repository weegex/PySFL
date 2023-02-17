import exception as e
import database as d
import field as f
import table as t
import type
import utils as u


database = d.Database(
    type.SQLITE3, u.Path(
        "sqlite3.db"
    )
)


class TestTable3(f.TableClass):
    test = f.TextField()
    test2 = f.IntegerField(primary_key=True)


table = database.addTable(TestTable3, True)


database.save()


# result = table.get(test="test")
# print(result.__dict__)
