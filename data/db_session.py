import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    # f'postgresql://postgres:2BoBa1Tolya@127.0.0.1:5432/postgres'
    conn_str = 'postgresql://qpnsqvnwwyyimk:7509fed8004a2c07d70467d00f6' \
               'dea9607b363dfde31cd56fa6e64072865d48f@ec2-3-91-127-228.co' \
               'mpute-1.amazonaws.com:5432/d4ncmqqmq5pi2v'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
