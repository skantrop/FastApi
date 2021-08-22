import sqlalchemy
import databases

# ядро генерирующее запросы
metadata = sqlalchemy.MetaData()
# название базы данных
database = databases.Database("sqlite:///sqlite.db")
engine = sqlalchemy.create_engine("sqlite:///sqlite.db")