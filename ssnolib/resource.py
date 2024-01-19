"""Implementation of classes
- dcat:Resource
- dcat:Distribution
- dcat:Dataset
"""
import pathlib
import re
from datetime import datetime
from typing import Union, List

from dateutil import parser
from pydantic import HttpUrl, FileUrl, field_validator

from .agent import Person, Organization
from .core import SSNOlibModel
from .utils import download_file


class Resource(SSNOlibModel):
    """Pyantic implementation of dcat:Resource

    .. note::

        More than the below parameters are possible but not explicitly defined here.



    Parameters
    ----------
    title: str
        Title of the resource (dcterms:title)
    description: str = None
        Description of the resource (dcterms:description)
    creator: Union[Person, Organization] = None
        Creator of the resource (dcterms:creator)
    version: str = None
        Version of the resource (dcat:version)
    """
    title: str  # dcterms:title
    description: str = None  # dcterms:description
    creator: Union[Person, Organization] = None  # dcterms:creator
    version: str = None  # dcat:version

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.title})"


class Distribution(Resource):
    """Implementation of dcat:Distribution

    .. note::
        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    downloadURL: Union[HttpUrl, FileUrl]
        Download URL of the distribution (dcat:downloadURL)
    mediaType: HttpUrl = None
        Media type of the distribution (dcat:mediaType).
        Should be defined by the [IANA Media Types registry](https://www.iana.org/assignments/media-types/media-types.xhtml)
    byteSize: int = None
        Size of the distribution in bytes (dcat:byteSize)
    """
    downloadURL: Union[HttpUrl, FileUrl]  # dcat:downloadURL, e.g.
    mediaType: HttpUrl = None  # dcat:mediaType
    byteSize: int = None  # dcat:byteSize

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.downloadURL})"

    def download(self, dest_filename: Union[str, pathlib.Path] = None,
                 overwrite_existing: bool = False) -> pathlib.Path:
        """Downloads the distribution"""
        if self.downloadURL.scheme == 'file':
            return pathlib.Path(self.downloadURL.path[1:])
        return download_file(self.downloadURL,
                             dest_filename,
                             overwrite_existing=overwrite_existing)

    @field_validator('mediaType', mode='before')
    @classmethod
    def _mediaType(cls, mediaType):
        """should be a valid URI, like: https://www.iana.org/assignments/media-types/text/markdown"""
        if isinstance(mediaType, str):
            if mediaType.startswith('http'):
                return HttpUrl(mediaType)
            elif mediaType.startswith('iana:'):
                return HttpUrl("https://www.iana.org/assignments/media-types/" + mediaType.split(":", 1)[-1])
            elif re.match('[a-z].*/[a-z].*', mediaType):
                return HttpUrl("https://www.iana.org/assignments/media-types/" + mediaType)
        return mediaType


class Dataset(Resource):
    """Pydantic implementation of dcat:Dataset

    .. note::

        More than the below parameters are possible but not explicitly defined here.



    Parameters
    ----------
    title: str
        Title of the resource (dcterms:title)
    description: str = None
        Description of the resource (dcterms:description)
    creator: Union[Person, Organization] = None
        Creator of the resource (dcterms:creator)
    version: str = None
        Version of the resource (dcat:version)
    identifier: HttpUrl = None
        Identifier of the resource (dcterms:identifier)
    contact: Union[Person, Organization] = None
        Contact person or organization of the resource (http://www.w3.org/ns/prov#Person)
    distribution: List[Distribution] = None
        Distribution of the resource (dcat:Distribution)
    modified: datetime = None
        Last modified date of the resource (dcterms:modified)
    """
    identifier: HttpUrl = None  # dcterms:identifier, see https://www.w3.org/TR/vocab-dcat-3/#ex-identifier
    # http://www.w3.org/ns/prov#Person, see https://www.w3.org/TR/vocab-dcat-3/#ex-adms-identifier
    contact: Union[Person, Organization] = None
    distribution: List[Distribution] = None  # dcat:Distribution
    modified: datetime = None  # dcterms:modified

    @field_validator('modified', mode='before')
    @classmethod
    def _modified(cls, modified):
        """parse datetime"""
        if isinstance(modified, str):
            return parser.parse(modified)
        return modified
