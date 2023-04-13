import tempfile
from pathlib import Path

import act
import pandas as pd
import xarray as xr

from src.utils.data_handlers.data_handler import DataHandler


class ARMHandler(DataHandler):

    @staticmethod
    def _process_cdf_file(file_path):
        # read in a netCDF file and convert it to a pandas DataFrame

        with xr.open_dataset(file_path) as ds:
            df = ds.to_dataframe()

        return df

    async def query(self):
        """
        Query Datastream
        """
        pass

    async def fetch_file(self):
        """
        Fetch Datastream file
        """
        pass

    async def _fetch_obj_from_arm(self, datastream, date):
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # https://arm-doe.github.io/ACT/API/generated/act.discovery.download_data.html
                files = act.discovery.download_data(self.arm_username, self.arm_auth_token, datastream, date, date,
                                                    output=tmp_dir)
            except Exception as e:
                raise ValueError(f"Could not fetch data from ARM: {str(e)}") from e

            # Process each netCDF file in the directory and concatenate the resulting DataFrames
            df_list = [self._process_cdf_file(file_path) for file_path in files]

        combined_df = pd.concat(df_list)
        data = combined_df.astype(str).to_dict(orient='records')

        return data

    async def _save_obj_to_ws(self, wsid, obj_data, provenance=None):
        pass

    def __init__(self, arm_username, arm_auth_token):
        super().__init__('ARM')
        self.arm_username, self.arm_auth_token = arm_username, arm_auth_token

    async def fetch_data(self, datastream, date):
        arm_data = await self._fetch_obj_from_arm(datastream, date)

        return arm_data

    async def save_data(self, file_path):
        pass
