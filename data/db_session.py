import os
import sqlalchemy as sa
import sqlalchemy.orm as orm
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import logging
from sqlalchemy.pool import NullPool


SqlAlchemyBase = dec.declarative_base()


__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    path = os.path.join(os.path.dirname(__package__), '.env')
    if os.path.exists(path):
        load_dotenv(path)
    try:
        sqlite = os.environ.get('SQLITE')
        if sqlite is None:
            raise AttributeError("param sqlite is 'NoneType'")
    except Exception as ex:
        logging.error(f'Probably not found .env file'
                      f'\nEXCEPTION: {ex}')
        return None
    conn_str = sqlite
    # conn_str = f'sqlite:///db/database.db?check_same_thread=False'
    # print(f"Подключение к базе данных по адресу {conn_str}")
    logging.info(f"Подключение к базе данных по адресу {conn_str}")
    engine = sa.create_engine(conn_str, echo=False, poolclass=NullPool)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
