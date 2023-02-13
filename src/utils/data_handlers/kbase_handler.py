from src.utils.data_handlers.data_handler import DataHandler
from src.utils.kbase_helpers.workspaceClient import Workspace


class KBaseHandler(DataHandler):

    async def _fetch_obj_from_ws(self, obj_ref):
        item = self.ws.get_objects2({'objects': [{'ref': obj_ref}],
                                     'no_data': 0})['data'][0]

        obj_info = item.get('info')
        obj_data = item.get('data')

        return obj_info, obj_data

    def __init__(self, auth_token, ws_url="https://kbase.us/services/ws"):
        super().__init__('KBase')
        self.auth_token = auth_token
        self.ws_url = ws_url
        try:
            self.ws = Workspace(url=self.ws_url, token=self.auth_token)
            self.ws.ver()
        except Exception as e:
            raise ValueError('Cannot connect to KBase Workspace client') from e

    async def fetch_data(self, pointer):
        obj_info, obj_data = await self._fetch_obj_from_ws(pointer)

        return obj_info, obj_data
