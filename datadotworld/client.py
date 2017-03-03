"""
data.world-py
Copyright 2017 data.world, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the
License.

You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.

This product includes software developed at data.world, Inc.(http://www.data.world/).
"""
import os
import re

import requests
from datadotworld._rest import ApiClient
from datadotworld._rest import DatasetsApi
from datadotworld._rest import UploadsApi

from datadotworld.models import (DatasetCreateRequest, DatasetPatchRequest, DatasetPutRequest,
                                       DatasetSummaryResponse, SuccessMessage, FileBatchUpdateRequest,
                                       FileCreateOrUpdateRequest, FileSourceCreateOrUpdateRequest, Results)
import requests
import csv
from io import StringIO
import datapackage
import zipfile
import io
import shutil
import pandas as pd

class DataDotWorld:
    """A Python Client for Accessing data.world"""

    def __init__(self, token=None, props_file="~/.data.world",
                 protocol="https",
                 query_host="query.data.world", api_host="api.data.world", download_host="download.data.world"):

        regex = re.compile(r"^token\s*=\s*(\S.*)$")
        filename = os.path.expanduser(props_file)
        self.token = token
        if self.token is None and os.path.isfile(filename):
            with open(filename, 'r') as props:
                self.token = next(iter([regex.match(line.strip()).group(1) for line in props if regex.match(line)]),
                                  None)
        if self.token is None:
            raise RuntimeError((
                'you must either provide an API token to this constructor, or create a '
                '.data.world file in your home directory with your API token'))

        self.protocol = protocol
        self.query_host = query_host

        self._api_client = ApiClient(host="{}://{}/v0".format(protocol, api_host), header_name='Authorization',
                                     header_value='Bearer {}'.format(token))
        self._datasets_api = DatasetsApi(self._api_client)
        self._uploads_api = UploadsApi(self._api_client)

        self._dataset_key_pattern = re.compile('[a-z0-9-]+/[a-z0-9-]+')  # Not the most comprehensive, for simplicity
        self.downloadHost=download_host

    # Dataset Operations

    def get_dataset(self, dataset_key):
        """Retrieve an existing dataset

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id

        Returns
        -------
        DatasetSummaryResponse
            The dataset object

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> intro_dataset = dw.get_dataset('jonloyens/an-intro-to-dataworld-dataset')
        >>> print(intro_dataset.description)
        A dataset that serves as a quick introduction to data.world and some of our capabilities.  Follow along in \
        the summary!
        """
        return self._datasets_api.get_dataset(*(self._split_dataset_key(dataset_key)))

    def create_dataset(self, owner_id, dataset):
        """Create a new dataset

        Parameters
        ----------
        owner_id : str
            Username of the owner of the new dataset
        dataset : DatasetCreateRequest
            The new dataset object

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> intro_dataset = DatasetCreateRequest()
        >>> intro_dataset.title = 'An intro to data.world dataset'
        >>> intro_dataset.visibility = 'OPEN'
        >>> intro_dataset.license = 'Public Domain License'
        >>> dw.create_dataset('jonloyens', intro_dataset)
        {'message': 'Dataset created successfully.'}
        """
        return self._datasets_api.create_dataset(owner_id, dataset)

    def patch_dataset(self, dataset_key, dataset):
        """Update an existing dataset

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id
        dataset : DatasetPatchRequest
            The dataset patch object, with only the attributes that need to change

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> intro_dataset_patch = DatasetPatchRequest()
        >>> intro_dataset_patch.tags = ['demo', 'datadotworld']
        >>> dw.patch_dataset('jonloyens/an-intro-to-dataworld-dataset', intro_dataset_patch)
        {'message': 'Dataset updated successfully.'}
        """
        owner_id, dataset_id = self._split_dataset_key(dataset_key)
        return self._datasets_api.patch_dataset(owner_id, dataset_id, dataset)

    def replace_dataset(self, dataset_key, dataset):
        """Replace an existing dataset

        *This method will completely overwrite an existing dataset.*

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id
        dataset : DatasetPutRequest
            The dataset object, redefining the entire dataset

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> intro_dataset_overwrite = DatasetPutRequest(
        >>>     description='A dataset that serves as a quick introduction to data.world',
        >>>     tags=['demo', 'datadotworld'],
        >>>     visibility='OPEN',
        >>>     license='Other')
        >>> dw.replace_dataset('jonloyens/an-intro-to-dataworld-dataset', intro_dataset_overwrite)
        {'message': 'Dataset replaced successfully.'}
        """
        owner_id, dataset_id = self._split_dataset_key(dataset_key)
        return self._datasets_api.replace_dataset(owner_id, dataset_id, dataset)

    # File Operations

    def add_files_via_url(self, dataset_key,
                          files):
        """Add or update dataset files linked to source URLs

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id
        files : list of FileCreateOrUpdateRequest
            The list of files to be added to the dataset or updated with a new URL

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> atx_basketball = FileCreateOrUpdateRequest(
        >>>     name='atx_startup_league_ranking.csv',
        >>>     source=FileSourceCreateOrUpdateRequest(
        >>>         url='http://www.atxsa.com/sports/basketball/startup_league_ranking.csv'))
        >>> dw.add_files_via_url('jonloyens/an-intro-to-dataworld-dataset',
        >>>                      FileBatchUpdateRequest(files=[atx_basketball]))
        {'message': 'Dataset successfully updated with new sources. Sync in progress.'}
        """
        owner_id, dataset_id = self._split_dataset_key(dataset_key)
        return self._datasets_api.add_files_by_source(owner_id, dataset_id, files)

    def sync_files(self, dataset_key):
        """Trigger synchronization process to update all dataset files linked to source URLs

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> dw.sync_files('jonloyens/an-intro-to-dataworld-dataset')
        {'message': 'Sync started.'}
        """
        return self._datasets_api.sync(*(self._split_dataset_key(dataset_key)))

    def upload_files(self, dataset_key, files):
        """Upload dataset files

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id
        files : list of str
            The list of names/paths for files stored in the local filesystem

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> dw.upload_files('jonloyens/an-intro-to-dataworld-dataset',
        >>>                 ['/Users/jon/DataDotWorldBBall/DataDotWorldBBallTeam.csv'])
        {'message': 'File(s) uploaded.'}
        """
        owner_id, dataset_id = self._split_dataset_key(dataset_key)
        return self._uploads_api.upload_files(owner_id, dataset_id, files)

    def delete_files(self, dataset_key, names):
        """Delete dataset file(s)

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id
        names : list of str
            The list of names for files to be deleted

        Returns
        -------
        SuccessMessage
            Short message indicating success of the operation

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> dw.delete_files('jonloyens/an-intro-to-dataworld-dataset', ['atx_startup_league_ranking.csv'])
        {'message': 'Dataset file(s) have been successfully deleted.'}
        """
        owner_id, dataset_id = self._split_dataset_key(dataset_key)
        return self._datasets_api.delete_files_and_sync_sources(owner_id, dataset_id, names)

    # Query Operations

    def query(self, dataset_key, query, query_type="sql"):
        """Query an existing dataset

        Parameters
        ----------
        dataset_key : str
            Dataset identifier, in the form of owner/id
        query : str
            SQL or SPARQL query
        query_type : {'sql', 'sparql'}, optional
            The type of the query. Must be either 'sql' or 'sparql'.

        Returns
        -------
        Results
            Object containing the results of the query

        Raises
        ------
        RuntimeError
            If a server error occurs

        Examples
        --------
        >>> results = dw.query('jonloyens/an-intro-to-dataworld-dataset',
        >>>                    'SELECT * FROM `DataDotWorldBBallStats`, `DataDotWorldBBallTeam` '
        >>>                    'WHERE DataDotWorldBBallTeam.Name = DataDotWorldBBallStats.Name')
        >>> df = results.as_dataframe()
        >>> df.info()
        <class 'pandas.core.frame.DataFrame'>
        RangeIndex: 8 entries, 0 to 7
        Data columns (total 6 columns):
        Name              8 non-null object
        PointsPerGame     8 non-null float64
        AssistsPerGame    8 non-null float64
        Name.1            8 non-null object
        Height            8 non-null object
        Handedness        8 non-null object
        dtypes: float64(2), object(4)
        memory usage: 456.0+ bytes
        """
        from . import __version__
        params = {
            "query": query
        }
        url = "{0}://{1}/{2}/{3}".format(self.protocol,
                                         self.query_host,
                                         query_type,
                                         dataset_key)
        headers = {
            'User-Agent': 'data.world-py - {0}'.format(__version__),
            'Accept': 'text/csv',
            'Authorization': 'Bearer {0}'.format(self.token)
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return Results(response.text)
        raise RuntimeError('error running query.')

    def _split_dataset_key(self, dataset_key):
        if not re.match(self._dataset_key_pattern, dataset_key):
            raise ValueError('Invalid dataset key. Key must include user and dataset names, separated by / '
                             '(i.e. user/dataset).')
        owner_id, dataset_id = dataset_key.split('/')
        return owner_id, dataset_id

    class Dataset:
        def __init__(self, dp):
            self.dp = dp
            self.table_names = [resource['name'] for resource in dp.descriptor['resources']]
            self.tables = {resource.descriptor['name']: DataDotWorld.Table(resource) for resource in self.dp.resources}

    class Table:
        def __init__(self, resource):
            self.resource = resource
            resource_descriptor = self.resource.descriptor
            self.table_dict = {"name": resource_descriptor["name"],
                               "columns": {field['name']: field for field in resource_descriptor['schema']['fields']}}

        def as_dataframe(self):
            df = pd.DataFrame(self.resource.data)
            for column in df.columns.values.tolist():
                datapackage_type=self.table_dict['columns'][column]['type']
                panda_type = DataDotWorld.Table.__convert_datapackage_type_to_panda_type(datapackage_type,
                                                                                         df[column].dtype)
                # print("{0} {1} {2}".format(column, datapackage_type , panda_type))
                df[[column]] = df[[column]].astype(panda_type)
            return df

        @staticmethod
        def __convert_datapackage_type_to_panda_type(type , defaul_type):
            if type == 'number':
                return float
            elif type == 'string':
                return str
            elif type == 'integer':
                return int
            elif type == 'boolean':
                return bool
            else:
                return defaul_type

        def data_dict(self):
            return self.table_dict

    def download_dataset(self, dataset, base_dir='./data/external/dw', overwrite=True):
        """Download dataset to local filesystem

        Parameters
        ----------
        dataset : str
            Dataset identifier, in the form of owner/id
        base_dir : str, optional
            Base directory under which to store downloaded dataset
        overwrite : boolean, optional
            true => the function will pull the latest content and overwrite the existing local cache

        Returns
        -------
        Dataset
            an object contain actual data and meta data of all dataset's tabular file

        Raises
        ------
        ApiException
            If a server error occurs

        Examples
        --------
        >>> intro_dataset = dw.download_dataset(dataset='jonloyens/an-intro-to-dataworld-dataset', overwrite=False)
        >>> intro_dataset.table_names
        ['anintrotodata.worlddatasetchangelog-sheet1', 'datadotworldbballstats', 'datadotworldbballteam']
        >>> table = intro_dataset.tables['datadotworldbballteam']
        >>> table_df = table.as_data_frame()
        """
        from . import __version__
        url = "{0}://{1}/datapackage/{2}".format(self.protocol, self.downloadHost, dataset)
        headers = {
            'User-Agent': 'data.world-py - {0}'.format(__version__),
            'Authorization': 'Bearer {0}'.format(self.token)
        }
        slugified_dataset = dataset.replace("/", "-")

        response = requests.get(url, headers=headers, stream=True)
        tmp_dir = "tmp"
        if response.status_code == 200:
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            z = zipfile.ZipFile(io.BytesIO(response.content))
            # extract to tmp
            z.extractall(path=tmp_dir)
            data_dir = "{0}/{1}".format(base_dir, dataset)
            if os.path.exists(data_dir):
                if overwrite:
                    shutil.rmtree(data_dir)
                    shutil.move("{0}/{1}".format(tmp_dir, slugified_dataset), data_dir)
            else:
                shutil.move("{0}/{1}".format(tmp_dir, slugified_dataset), data_dir)
            dp = DataDotWorld.__get_datapackage(dataset, base_dir=base_dir)
            return DataDotWorld.Dataset(dp)
        else:
            raise RuntimeError("error download dataset. {0}".format(response.status_code))

    @staticmethod
    def __get_datapackage_path(dataset, base_dir='./data/external/dw'):
        """internal util method to get local filesystem path to the datapackage json file

        Parameters
        ----------
        dataset : str
            Dataset identifier, in the form of owner/id

        Returns
        -------
        path
            a local file path

        Raises
        ------
        RuntimeError
            if a dataset is invalid or a dataset has not been downloaded yet locally

        """
        cwd = os.getcwd()
        path = os.path.join(cwd, base_dir, dataset, "datapackage.json")
        if os.path.isfile(path):
            return path
        else:
            raise RuntimeError("datapackage for {0} is not at {1}".format(dataset, path))

    @staticmethod
    def __get_datapackage(dataset, base_dir='./data/external/dw'):
        """internal util method to get a DataPackage Object (http://frictionlessdata.io/data-packages/)

        Parameters
        ----------
        dataset : str
            Dataset identifier, in the form of owner/id

        Returns
        -------
        a DataPackage object

        Raises
        ------
        RuntimeError
            if a dataset is invalid or a dataset has not been downloaded yet locally

        """
        datapackage_path = DataDotWorld.__get_datapackage_path(dataset, base_dir=base_dir)
        dp = datapackage.DataPackage(datapackage_path)
        return dp

    @staticmethod
    def __load_table_from_datapackage(datapackage, table_name, limit=None):
        """internal util method to load a table from a cached data package

        Parameters
        ----------
        dataset : str
            Dataset identifier, in the form of owner/id
        table_name : str
            name of a table belonged in the dataset
        limit : int
            how many rows included in the result set, default to None which mean all rows
        Returns
        -------
        a DataPackage object

        Raises
        ------
        RuntimeError
            if a dataset is invalid or a dataset has not been downloaded yet locally

        """
        resource = next((x for x in datapackage.resources if x.descriptor['name'] == table_name), None)
        if resource is None:
            print("table {0} is not found".format(table_name))
        else:
            if limit is None:
                return pd.DataFrame(resource.data)
            else:
                return pd.DataFrame(resource.data[0:limit])
