import os

from . import request_acquisition
from . import storage
from . import storage_sqlalchemy


pipeline = request_acquisition.RequestPreprocessingPipeline()


def choose_correct_store():
    store = storage.MemoryRequestsStorage()
    if "SQLITE_FILE" in os.environ:
        sqlite_file = os.environ["SQLITE_FILE"]
        store = storage_sqlalchemy.SqlAlchemyRequestStorage(
            f"sqlite:///{sqlite_file}")
    if "POSTGRES_USER" in os.environ:
        username = os.environ["POSTGRES_USER"]
        password = os.environ["POSTGRES_PASSWORD"]
        store = storage_sqlalchemy.SqlAlchemyRequestStorage(
            f"postgresql+psycopg2://{username}:{password}@postgres/{username}")
    return store


chosen_storage = choose_correct_store()
pipeline.add_block('activity', request_acquisition.UIDAssigner())
pipeline.add_block('activity', request_acquisition.Saver(chosen_storage))
pipeline.add_block('cancel', request_acquisition.Canceller(chosen_storage))
