from src.utils.data_handlers.data_handler import DataHandler


class Dataverse:

    def __init__(self):
        self.handlers = {}

    def register_handler(self, handler_id: str, handler: DataHandler):
        self.handlers[handler_id] = handler

    def handler(self, handler_id: str, handler: DataHandler):

        pass

    def list_handlers(self):
        return list(self.handlers)

    def resolve_path(self, handler_id, **kwargs):
        auth = {
            'token': kwargs.get('token', None),
            'user': kwargs.get('user', None)
        }
        if handler_id in self.handlers:
            _h = self.handlers[handler_id](**auth)
            return _h.fetch_data(**kwargs)
        else:
            raise Exception(f'Error! {self.handlers.keys()}')
