import sqlite3
import asyncio
from .worker import AsyncWorker

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class AsyncIteratorWrapper:
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


class AsyncContextWrapper:
    def __init__(self, Context):
        self._Context = Context

    async def __aenter__(self):
        return self._Context.__enter__()

    async def __aexit__(self, exc_type, exc, tb):
        return self._Context.__exit__(exc_type, exc, tb)


def sqlConn(name):
    conn = sqlite3.connect(name)
    conn.row_factory = dict_factory
    return conn


def AsyncConn(name):
    return AsyncContextWrapper(sqlConn(name))


class whereObj:
    def __init__(self, *args, **kwargs):
        self.whereConditions = ""
        if len(args) is not 0:
            # focus on args
            self.whereConditions += "args[1]"
        else:
            # focus on kwargs
            self._and(**kwargs)

    def _or(self, *args, **kwargs):
        if len(args) is not 0:
            # focus on args
            self.whereConditions += f" OR {args[0]}"
        else:
            # focus on kwargs
            for key, val in kwargs.items():
                self.whereConditions += f" OR {key} = {val}" if val.isdigit() else f" OR {key} = '{val}'"
        return self

    def _and(self, *args, **kwargs):
        if len(args) is not 0:
            # focus on args
            self.whereConditions += f" AND {args[0]}"
        else:
            # focus on kwargs
            for key, val in kwargs.items():
                if(self.whereConditions is not ""):
                    self.whereConditions += " AND"
                self.whereConditions += f" {key} = " + f"{val}" if val.isdigit() else f"'{val}'"
        return self

    def _eql(self, e):
        self.whereConditions += f" = {e}"
        return self

    def _like(self, v):
        self.whereConditions += f" LIKE '{e}'"
        return self

    def _glob(self, g):
        self.whereConditions += f" GLOB '{e}'"
        return self


class queryObj:
    def __init__(self, coroutine, tableNmae, *args):
        self.coro = coroutine
        self.where = None
        self.orderConditions = ""
        columns = ", ".join(args) if (
            len(args) is not 0) or (args is None) else "*"
        self.res = SqlKit.SELECT.format(columns, tableNmae)

    def orderBy(self, ASC, *args):
        self.orderConditions = ",".join(args)
        self.orderConditions += " ASC" if ASC else " DESC"
        return self

    def where(self, *args, **kwargs):
        self.where = whereObj(self, *args, **kwargs)
        self.where.result = self.result
        self.where.orderBy = self.orderBy
        return self.where

    def result(self):
        res = self.res
        if self.where:
            res += SqlKit.WHERE.format(self.where.whereConditions)
        if self.orderConditions is not "":
            res += " ORDER BY "
            res += self.orderConditions
        task = self.coro(res)
        return AsyncWorker().wait(task)


class deleteObj:
    def __init__(self, coroutine, tableNmae):
        self.coro = coroutine
        self.where = None
        self.res = SqlKit.DELETE.format(tableNmae)

    def where(self, *args, **kwargs):
        self.where = whereObj(self, *args, **kwargs)
        self.where.delete = self.delete
        return self.where

    def result(self):
        res = self.res
        if self.where:
            res += SqlKit.WHERE.format(self.where.whereConditions)
        task = self.coro(res)
        return AsyncWorker().wait(task)


class updataObj:
    def __init__(self, coroutine, tableNmae):
        self.coro = coroutine
        self.where = None
        self.res = SqlKit.UPDATE.format(tableNmae)
        self._data = []
        self.dataConditions = ""

    def where(self, *args, **kwargs):
        self.where = whereObj(self, *args, **kwargs)
        self.where.result = self.result
        return self.where

    def data(self, **kwargs):
        for key, val in kwargs.items():
            self.dataConditions += f" {key} = ? ,"
            self._data.append(val)
        self.dataConditions = self.dataConditions[:-1]
        return self

    def result(self):
        res = self.res
        if self.where:
            res += SqlKit.WHERE.format(self.where.whereConditions)
        task = self.coro(res + self.dataConditions, self._data)
        return AsyncWorker().wait(task)


class insertObj:
    def __init__(self, coroutine, tableNmae):
        self.tbName = tableNmae
        self.coro = coroutine
        self.res = ""
        self._data = []
        self.dataConditions = ""
        self.valConditions = ""

    def data(self, **kwargs):
        for key, val in kwargs.items():
            self.dataConditions += f" {key},"
            self.valConditions += f"?,"
            self._data.append(val)
        self.dataConditions = self.dataConditions[:-1]
        self.valConditions = self.valConditions[:-1]
        return self

    def result(self):
        res = SqlKit.INSERT.format(
            self.tbName, self.dataConditions, self.valConditions)
        task = self.coro(res, self._data)
        return AsyncWorker().wait(task)


class SqlKit:
    # INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
    # VALUES (1, 'Paul', 32, 'California', 20000.00 );
    INSERT = "INSERT INTO {} ({}) VALUES ({})"
    WHERE = " WHERE {}"
    SELECT = "SELECT {} FROM {}"
    DELETE = "DELETE FROM {}"
    UPDATE = "UPDATE {} SET"
