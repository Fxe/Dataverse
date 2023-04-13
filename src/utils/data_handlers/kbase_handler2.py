import copy

from src.utils.data_handlers.data_handler import DataHandler
from src.utils.kbase_helpers.workspaceClient import Workspace as WorkspaceClient


def _process_workspace_identifiers(id_or_ref, workspace=None):
    """
    IDs should always be processed through this function so we can interchangeably use
    refs, IDs, and names for workspaces and objects
    """
    obj_spec = {}
    if workspace is None:
        obj_spec["ref"] = id_or_ref
    else:
        if isinstance(workspace, int):
            obj_spec["wsid"] = workspace
        else:
            obj_spec["workspace"] = workspace
        if isinstance(id_or_ref, int):
            obj_spec["objid"] = id_or_ref
        else:
            obj_spec["name"] = id_or_ref
    return obj_spec


class KBaseHandler2(DataHandler):

    def _fetch_obj_from_ws(self, id_or_ref, workspace=None):
        try:
            item = self.ws.get_objects2({'objects': [_process_workspace_identifiers(id_or_ref, workspace)],
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

    def __init__(self, **kwargs):
        super().__init__('KBase')
        self.auth_token = kwargs.get('token', None)
        self.ws_url = kwargs.get('ws_url', 'https://kbase.us/services/ws/')
        self.ws_handle_url = kwargs.get('ws_handle_url', 'https://kbase.us/services/handle_service')
        # KBASE_WS_URL = "https://kbase.us/services/ws/"
        # KBASE_HANDLE_URL = "https://kbase.us/services/handle_service"
        try:
            self.ws = WorkspaceClient(url=self.ws_url, token=self.auth_token)
            self.ws.ver()
        except Exception as e:
            raise ValueError(f'Cannot connect to KBase Workspace client: {e}') from e

    def fetch_data(self, **kwargs):
        ws_id = kwargs.get('path', None)
        object_id = kwargs.get('object_id', None)
        version = kwargs.get('version', None)
        print(ws_id, object_id, version)

        if ws_id is None:  # list workspace if no ws
            res = self.ws.list_workspace_info({})
            return [{'id': o[1], 'd': o[8]['narrative_nice_name'], 'owner': o[2], 't': o[3], 'type': 'folder'} for o in
                    res if 'narrative_nice_name' in o[8]]
        elif object_id is None:  # list workspace objects if no object_id
            res = self.ws.list_workspace_objects({'workspace': ws_id})
            return [{'id': o[0], 'd': o[0], 'owner': o[5], 't': o[2], 'type': 'file'} for o in res if
                    not o[1].startswith('KBaseNarrative.Narrative')]
        elif version is None:  # get object lastest version
            obj_info, obj_data = self._fetch_obj_from_ws(object_id, ws_id)
            return [{'id': object_id, 'type': 'data', 'data': [obj_info, obj_data]}]
            pass
        else:  # get exact object version
            raise Exception('Not implemented')

    async def save_data(self, wsid, obj_data, provenance=None):

        obj_info = await self._save_obj_to_ws(wsid, obj_data, provenance=provenance)

        obj_ref = f"{obj_info[6]}/{obj_info[0]}/{obj_info[4]}"

        return obj_ref, obj_info