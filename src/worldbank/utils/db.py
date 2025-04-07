import os
from pathlib import Path
from typing import cast, Dict, TypedDict
from psycopg.abc import Query
from psycopg import sql
import psycopg
from contextlib import contextmanager


@contextmanager
def postgres_context():
    with psycopg.connect(**postgres_options) as connection:
        with connection.cursor() as cursor:
            yield (connection, cursor)


postgres_options = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "root",
    "host": "backtesting-workshop-postgres",
    "port": 5432,
}


class QuerySpec:
    def __init__(self, abspath: Path, filename: str):
        self.abspath = abspath
        self.filename = filename
        self.specs = self.build_specs()

    def get_name(self):
        return self.specs["name"]

    def build_specs(self):
        name = "-".join(self.filename.split(".")[0:-1])
        file_abspath = self.abspath / self.filename
        with open(file_abspath, "r") as f:
            sql = cast(Query, f.read())
        return {
            "name": name,
            "filename": self.filename,
            "abspath": file_abspath,
            "sql": sql,
        }

    def __conform__(self, protocol) -> Query:
        if protocol is sql.Composable:
            return self.specs["sql"]
        else:
            raise TypeError("Only Query")


# Maybe it's possible to create a __str__ like function that will
# be called when Query type is needed.
class QuerySpecType(TypedDict):
    name: str
    filename: str
    abspath: Path
    sql: Query


QuerySpecTypes = Dict[str, QuerySpecType]
QuerySpecClasses = Dict[str, QuerySpec]


def get_query_spec(abspath: Path, filename: str) -> QuerySpecType:
    name = ".".join(filename.split(".")[0:-1])
    file_abspath = abspath / filename
    with open(file_abspath, "r") as f:
        sql = cast(Query, f.read())
    return {
        "name": name,
        "filename": filename,
        "abspath": file_abspath,
        "sql": sql,
    }


def get_queries_by_type(relpath: str) -> QuerySpecTypes:
    path = "/".join(__file__.split("/")[0:-1])
    abspath = Path(os.path.abspath(path)) / "../sql" / relpath
    all_files = os.listdir(abspath)
    sql_files = [f for f in all_files if f.endswith(".sql")]
    query_specs: QuerySpecTypes = dict()
    for sql_file in sql_files:
        spec = get_query_spec(abspath, sql_file)
        query_specs[spec["name"]] = spec

    return query_specs


def get_queries_by_class(relpath: str) -> QuerySpecClasses:
    path = "/".join(__file__.split("/")[0:-1])
    abspath = Path(os.path.abspath(path)) / "../sql" / relpath
    all_files = os.listdir(abspath)
    sql_files = [f for f in all_files if f.endswith(".sql")]
    query_specs: QuerySpecClasses = dict()
    for sql_file in sql_files:
        spec = QuerySpec(abspath, sql_file)
        query_specs[spec.get_name()] = spec

    return query_specs


def exec(name, args=()):
    sql = get_queries_by_type("gdp")
    with postgres_context() as (con, cur):
        cur.execute(sql[name]["sql"], args)


def select(name, args=()):
    sql = get_queries_by_type("gdp")
    with postgres_context() as (con, cur):
        cur.execute(sql[f"select.{name}"]["sql"], args)
        response = cur.fetchall()
        return response


def query(sql, args=()):
    with postgres_context() as (con, cur):
        cur.execute(cast(Query, sql), args)
