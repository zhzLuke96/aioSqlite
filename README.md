# aioSqlite
 Sqlite work for asyncio

# Useage
```python
db = sql("./db/test.db")
user_table = db.table("USER")
```
init is ez

### QUERY
```python
res = await user_table.query("id","name","mail").where(id=1).result()
```
SQL: SELECT ID,NAME,MAIL FROM USER WHERE ID = 1;

```python
res = await user_table.queryAll().orderBy(False, "time", "id").result()
```
SQL: SELECT * FROM USER ORDER BY TIME, ID DESC;
```python
res = await user_table.queryAll().where("name").like("%evil%").result()
```
SQL: SELECT * FROM USER LIKE '%evil%';
```python
res = await user_table.queryAll().limit(10).offset(11).result()
```
SQL: SELECT * FROM USER LIMIT 10 OFFSET 11;
```python
res = await user_table.queryAll()
            .where("name").like("%evil%")
            .orderBy(False, "time")
            .limit(10).offset(11)
            .result()
```
cool...
### INSTER
```python
res = await user_table.insert(id=1,name="huahua",emil="DEFAULT")
# or
res = await user_table.insert().data(id=1,name="huahua",emil="DEFAULT").result()
```
SQL: INSERT INTO USER (id, name, emil)
VALUES (1, "huahua", "DEFAULT");

### DELETE
```python
res = await user_table.delete(id=1,name="huahua")
# or
res = await user_table.delete().where(id=1,name="huahua").result()
```
SQL: DELETE FROM USER WHERE ID = 1, NAME = "huahua";

# todo
If free, have time...
