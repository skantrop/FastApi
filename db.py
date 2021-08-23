import sqlalchemy
import databases

# ядро генерирующее запросы
metadata = sqlalchemy.MetaData()
# название базы данных
database = databases.Database("sqlite:///mysqlite.db")
engine = sqlalchemy.create_engine("sqlite:///mysqlite.db")