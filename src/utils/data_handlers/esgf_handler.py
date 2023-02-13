from src.utils.data_handlers.data_handler import DataHandler


class ESGFHandler(DataHandler):

    def __init__(self):
        super().__init__('ESGF')

    def fetch_data(self, pointer):
        pass
