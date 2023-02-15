import pandas as pd
import xarray as xr

from src.utils.data_handlers.data_handler import DataHandler
from src.utils.esgf_helpers.esgf_helper import esgf_search


class ESGFHandler(DataHandler):

    @staticmethod
    def _process_cdf_file(file_path):
        # read in a netCDF file and convert it to a pandas DataFrame

        with xr.open_dataset(file_path) as ds:
            df = ds.to_dataframe()

        return df

    async def _fetch_obj_from_esgf(self, datastream, date):
        try:
            # https://projectpythia.org/cmip6-cookbook/notebooks/foundations/esgf-opendap.html
            files = esgf_search(activity_id='CMIP', table_id='Amon', variable_id='tas', experiment_id='historical',
                                institution_id="NCAR", source_id="CESM2", member_id="r10i1p1f1")

        except Exception as e:
            raise ValueError(f"Could not fetch data from ARM: {str(e)}") from e

        # with xr.open_mfdataset(files, combine='by_coords') as ds:
        #     df = ds.to_dataframe()

        df_list = [self._process_cdf_file(file_path) for file_path in files]
        combined_df = pd.concat(df_list)

        data = combined_df.astype(str).to_dict(orient='records')

        return data

    async def _save_obj_to_ws(self, wsid, obj_data, provenance=None):
        pass

    def __init__(self):
        super().__init__('ESGF')

    async def fetch_data(self, datastream, date):
        arm_data = await self._fetch_obj_from_esgf(datastream, date)

        return arm_data

    async def save_data(self, file_path):
        pass
