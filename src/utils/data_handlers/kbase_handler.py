import copy

from src.utils.data_handlers.data_handler import DataHandler
from src.utils.kbase_helpers.workspaceClient import Workspace


def _sort_dict(in_struct):
    """
    Recursively sort a dictionary by dictionary keys.
    """
    if isinstance(in_struct, dict):
        return {k: _sort_dict(in_struct[k]) for k in sorted(in_struct)}
    elif isinstance(in_struct, list):
        return [_sort_dict(k) for k in in_struct]
    else:
        return in_struct


class KBaseHandler(DataHandler):

    async def _fetch_obj_from_ws(self, obj_ref):
        try:
            item = self.ws.get_objects2({'objects': [{'ref': obj_ref}],
                                         'no_data': 0})['data'][0]
        except Exception as e:
            raise ValueError(f"Could not fetch object from workspace: {str(e)}") from e

        obj_info = item.get('info')
        obj_data = item.get('data')

        return obj_info, obj_data

    async def _save_obj_to_ws(self, wsid, obj_data, provenance=None):
        obj_to_save = {}

        prov_to_save = provenance
        if 'extra_provenance_input_refs' in obj_data:
            # need to make a copy so we don't clobber other objects
            prov_to_save = copy.deepcopy(provenance)
            extra_input_refs = obj_data['extra_provenance_input_refs']
            if extra_input_refs:
                if len(provenance) > 0:
                    if 'input_ws_objects' in provenance[0]:
                        prov_to_save[0]['input_ws_objects'].extend(extra_input_refs)
                    else:
                        prov_to_save[0]['input_ws_objects'] = extra_input_refs
                else:
                    prov_to_save = [{'input_ws_objects': extra_input_refs}]

        keys = ['type', 'name', 'objid', 'meta', 'hidden']
        obj_to_save.update({k: obj_data[k] for k in keys if k in obj_data})

        if 'data' in obj_data:
            obj_to_save['data'] = _sort_dict(obj_data['data'])

        obj_to_save['provenance'] = prov_to_save

        try:
            obj_info = self.ws.save_objects({'id': wsid, 'objects': [obj_to_save]})[0]
        except Exception as e:
            raise ValueError(f"Could not save object to workspace: {str(e)}") from e

        return obj_info

    def __init__(self, auth_token, ws_url="https://ci.kbase.us/services/ws"):
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

    async def save_data(self, wsid, obj_data, provenance=None):

        obj_info = await self._save_obj_to_ws(wsid, obj_data, provenance=provenance)

        obj_ref = f"{obj_info[6]}/{obj_info[0]}/{obj_info[4]}"

        return obj_ref, obj_info
