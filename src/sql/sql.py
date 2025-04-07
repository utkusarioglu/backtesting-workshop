#!/opt/conda/envs/econ/bin/python

from typing import cast
from psycopg.abc import Query
import psycopg

SQL_PATH = "src/sql/test"

queries = {}


def main():
    with open(f"{SQL_PATH}/table.sql", "r") as f:
        table = cast(Query, f.read())

    with open(f"{SQL_PATH}/insert.sql", "r") as f:
        insert = cast(Query, f.read())

    with open(f"{SQL_PATH}/select.sql", "r") as f:
        select = cast(Query, f.read())

    with psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="root",
        host="backtesting-workshop-postgres",
        port=5432,
    ) as conn:

        with conn.cursor() as c:
            print("Creating")
            c.execute(table, ())

        with conn.cursor() as c:
            print("inserting")
            c.executemany(
                # insert,
                insert,
                [
                    {
                        "name": "meow",
                        "age": 2,
                    },
                    {
                        "name": "fairy",
                        "age": 333,
                    },
                    {
                        "name": "rita",
                        "age": 22,
                    },
                ],
            )

        with conn.cursor() as c:
            print("selecting")
            c.execute(select, ())
            resp = c.fetchall()
            print(resp)


if __name__ == "__main__":
    print("Running")
    main()
    print("Done")
