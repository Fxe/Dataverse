import requests

from src.utils.data_handlers.data_handler import DataHandler
from urllib.request import urlopen

import datetime as dt


# from act.utils
def date_parser(date_string, output_format='%Y%m%d', return_datetime=False):
    """Converts one datetime string to another or to
    a datetime object.

    Parameters
    ----------
    date_string : str
        datetime string to be parsed. Accepted formats are
        YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY or YYYYMMDD.
    output_format : str
        Format for datetime.strftime to output datetime string.
    return_datetime : bool
        If true, returns str as a datetime object.
        Default is False.

    returns
    -------
    datetime_str : str
        A valid datetime string.
    datetime_obj : datetime.datetime
        A datetime object.

    """
    date_fmts = [
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%d/%m/%Y',
        '%Y%m%d',
        '%Y/%m/%d',
        '%Y-%m-%dT%H:%M:%S',
        '%d.%m.%YT%H:%M:%S',
        '%d/%m/%YT%H:%M:%S',
        '%Y%m%dT%%H:%M:%S',
        '%Y/%m/%dT%H:%M:%S',
    ]
    for fmt in date_fmts:
        try:
            datetime_obj = dt.datetime.strptime(date_string, fmt)
            if return_datetime:
                return datetime_obj
            else:
                return datetime_obj.strftime(output_format)
        except ValueError:
            pass
    fmt_strings = ', '.join(date_fmts)
    raise ValueError('Invalid Date format, please use one of these formats ' + fmt_strings)


class ARMHandler2(DataHandler):

    @staticmethod
    def _process_cdf_file(file_path):
        # read in a netCDF file and convert it to a pandas DataFrame

        with xr.open_dataset(file_path) as ds:
            df = ds.to_dataframe()

        return df

    def _fetch_file(self, fname):
        save_data_url = (
                'https://adc.arm.gov/armlive/livedata/' + 'saveData?user={0}&file={1}'
        ).format(':'.join([self.auth_user, self.auth_token]), fname)
        data = urlopen(save_data_url).read()
        return [{'id': fname, 'type': 'data', 'data': data}]

    def _fetch_datastream(self, datastream, date_start=None, date_end=None):
        from datetime import timedelta
        # default start and end are empty
        start, end = '', ''
        # start and end strings for query_url are constructed
        # if the arguments were provided
        if date_start:
            start_datetime = date_parser(date_start, return_datetime=True)
            start = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            start = f'&start={start}'
            if date_end:
                end_datetime = date_parser(date_end, return_datetime=True)
                # If the start and end date are the same, and a day to the end date
                if start_datetime == end_datetime:
                    end_datetime += timedelta(hours=23, minutes=59, seconds=59)
                end = end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                end = f'&end={end}'
        # print(datastream, start, end)
        query_url = (
                'https://adc.arm.gov/armlive/livedata/query?' + 'user={0}&ds={1}{2}{3}&wt=json'
        ).format(':'.join([self.auth_user, self.auth_token]), datastream, start, end)
        # print(query_url)
        response = requests.get(query_url)
        if response.status_code == 200:
            response_body_json = response.json()
            if 'files' in response_body_json:
                return [{'id': s, 'd': s, 'owner': 'nan', 't': 'nan', 'type': 'file'} for s in
                        response_body_json['files']]
            else:
                raise ValueError(f"Could not fetch data from ARM: no files returned")
        else:
            raise ValueError(f"Could not fetch data from ARM: status {response.status_code}")

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

    def __init__(self, **kwargs):
        super().__init__('ARM')
        self.auth_token = kwargs.get('token', None)
        self.auth_user = kwargs.get('user', None)
        # self.arm_username, self.arm_auth_token = arm_username, arm_auth_token

    def fetch_data(self, **kwargs):
        datastream = kwargs.get('datastream', None)
        date_start = kwargs.get('date_start', None)
        date_end = kwargs.get('date_end', None)
        file = kwargs.get('object_id', None)
        if file is None:
            return self._fetch_datastream(datastream, date_start, date_end)
        else:
            return self._fetch_file(file)
