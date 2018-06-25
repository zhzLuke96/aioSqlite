import sqlite3
import asyncio
from .util import deleteObj, insertObj, updataObj, queryObj, AsyncConn
# from .worker import AsyncWorker

class _sql:
    _SQLNAME = ""

    def __init__(self, dbNAME):
        self._SQLNAME = dbNAME

    # def _cursor(self):
    #     return AsyncConnect(self._SQLNAME).cursor()

    async def create_table(self, sqlScript):
        # async with AsyncConnect(self._SQLNAME) as conn:
        async with AsyncConn(self._SQLNAME) as conn:
            c = conn.cursor()
            c.execute(sqlScript)

    async def execute(self, s, vals=[]):
        res = None
        # async with AsyncConnect(self._SQLNAME) as conn:
        async with AsyncConn(self._SQLNAME) as conn:
            c = conn.cursor()
            # await asyncio.sleep(10)
            c.execute(s, vals)
            res = c.fetchall()
        return res

    def insert(self, tableName, **kwargs):
        obj = insertObj(self.execute, tableName)
        if kwargs:
            return obj.data(**kwargs).result()
        return obj

    def query(self, tableName, *args):
        return queryObj(self.execute, tableName, *args)

    def queryAll(self, tableName):
        return queryObj(self.execute, tableName)

    def updata(self, tableName, **kwargs):
        obj = updataObj(self.execute, tableName)
        if kwargs:
            return obj.where(**kwargs)
        return obj

    def delete(self, tableName, **kwargs):
        obj = deleteObj(self.execute, tableName)
        if kwargs:
            return obj.where(**kwargs).delete()
        return obj


class _table:
    _db = None
    _tableName = ""
    _newData = None
    # _worker = ThreadWorker()

    def __init__(self, sqlobj, tbName):
        self._db = sqlobj
        self._tableName = tbName

    def insert(self, **kwargs):
        return self._db.insert(self._tableName, **kwargs)

    def query(self, *args):
        return self._db.query(self._tableName, *args)

    def queryAll(self):
        return self._db.queryAll(self._tableName)

    async def updata(self, **kwargs):
        await self._db.updata(self._tableName, **kwargs)

    def delete(self, **kwargs):
        return self._db.delete(self._tableName, **kwargs)

    def quit(self):
        pass


class aioSql:
    def __init__(self, dbNAME):
        self._manager = _sql(dbNAME)

    def table(self, _name):
        return _table(self._manager, _name)
