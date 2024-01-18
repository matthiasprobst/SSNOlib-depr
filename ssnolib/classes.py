"""Classes of the ssno ontology"""
import abc
import json
import pathlib
import warnings
from datetime import datetime
from typing import List, Union, Dict

import pydantic
import rdflib
from pydantic import BaseModel, HttpUrl
from pydantic import EmailStr

from . import plugins
from .context import SSNO as SSNO_CONTEXT_URL
from .utils import download_file

standard_name_table: str


class _Core(abc.ABC):

    @abc.abstractmethod
    def _repr_html_(self):
        """Returns the HTML representation of the class"""


class Resource(BaseModel, _Core):
    """dcat:Resource"""
    title: str  # dcterms:title
    description: str = None  # dcterms:description
    creator: str = None  # dcterms:creator
    version: str = None  # dcat:version

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.title})"


class Distribution(Resource):
    """dcat:Distribution"""
    downloadURL: Union[str, HttpUrl]  # dcat:downloadURL, e.g.
    mediaType: str = None  # dcat:mediaType
    byteSize: int = None  # dcat:byteSize

    @pydantic.field_validator('downloadURL')
    @classmethod
    def _downloadURL(cls, downloadURL):
        """Validates the downloadURL field"""
        if downloadURL is None:
            return None
        else:
            return str(HttpUrl(downloadURL))

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.downloadURL})"

    def download(self, dest_filename: Union[str, pathlib.Path] = None,
                 overwrite_existing: bool = False):
        """Downloads the distribution"""
        return download_file(self.downloadURL,
                             dest_filename,
                             overwrite_existing=overwrite_existing)


class Contact(BaseModel):
    first_name: str = None  # foaf:firstName
    last_name: str = None  # foaf:lastName
    mbox: EmailStr = None  # foaf:mbox
    identifier: HttpUrl = None  # dcterms:identifier

    @pydantic.field_validator('identifier')
    @classmethod
    def _identifier(cls, identifier):
        return str(identifier)


class Dataset(Resource):
    """dcat:Dataset"""
    identifier: HttpUrl = None  # dcterms:identifier, see https://www.w3.org/TR/vocab-dcat-3/#ex-identifier
    contact: Contact = None  # http://www.w3.org/ns/prov#Person, see https://www.w3.org/TR/vocab-dcat-3/#ex-adms-identifier
    distribution: List[Distribution] = None  # dcat:Distribution
    modified: datetime = None  # dcterms:modified

    @pydantic.field_validator('modified')
    @classmethod
    def _modified(cls, modified):
        if not isinstance(modified, str):
            from dateutil import parser
            return parser.parse(modified)
        return modified

    @pydantic.field_validator('identifier')
    @classmethod
    def _identifier(cls, identifier):
        return str(identifier)


class StandardName(BaseModel, _Core):
    """Implementation of ssno:StandardNmae"""
    standard_name: str
    canonical_units: Union[str, None]
    description: str  # dcterms:description
    dbpedia_match: Union[str, HttpUrl] = None  # ssno:dbpediaMatch
    standard_name_table: Dataset = None  # ssno:standard_name_table (subclass of dcat:Dataset)

    @pydantic.field_validator('description')
    @classmethod
    def _description(cls, description):
        if description is None:
            warnings.warn("The description should not be None. Please make sure to provide a description. For "
                          "now, an empty string is used.")
            return ""
        return description

    @pydantic.field_validator('canonical_units')
    @classmethod
    def _canonical_units(cls, canonical_units):
        """Validates the downloadURL field"""
        if canonical_units is None:
            return ""
        return canonical_units

    def __str__(self):
        """Returns the standard name"""
        return self.standard_name

    def dump_dict(self, *args, **kwargs):
        """alias for model_dump()"""
        return self.model_dump(*args, **kwargs)

    def dump_json(self, *args, **kwargs):
        """alias for model_dump_json()"""
        return self.model_dump_json(*args, **kwargs)

    def dump_jsonld(self, id=None, *args, **kwargs):
        """alias for model_dump_json()"""

        g = rdflib.Graph()
        _atemp_json_dict = {k.replace('_', ' '): v for k, v in self.model_dump().items()}

        _qudt_unit_dict = {"K": "https://qudt.org/vocab/unit/K"}

        _atemp_json_dict['canonical units'] = _qudt_unit_dict.get(_atemp_json_dict['canonical units'],
                                                                  _atemp_json_dict['canonical units'])

        _id = '_:' or id
        jsonld = {"@context": {"@import": SSNO_CONTEXT_URL},
                  "@graph": [
                      {"@id": _id,
                       "@type": "ssno:StandardName",
                       **_atemp_json_dict}
                  ]}

        g.parse(data=json.dumps(jsonld), format='json-ld')
        return g.serialize(format='json-ld',
                           context={"@import": SSNO_CONTEXT_URL},
                           indent=4)

    @pydantic.field_validator('dbpedia_match')
    @classmethod
    def _dbpedia_match(cls, url):
        """Validates the dbpedia_match"""
        if url is None:
            return None
        else:
            return str(HttpUrl(url))

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return self.standard_name


class StandardNameTable(Dataset):
    """Implementation of ssno:StandardNameTable

    Parameters
    ----------
    title: str
        Title of the Standard Name Table (dcterms:title)
    description: str
        Description of the Standard Name Table (dcterms:description)
    contact: str
        Contact Person (http://www.w3.org/ns/prov#Person)
    modified: datetime
        Date of the last modification of the Standard Name Table (dcterms:modified)
    version: str
        Version of the Standard Name Table (dcat:version)
    identifier: str
        Identifier of the Standard Name Table, e.g. the DOI (dcterms:identifier)
    standard_names: List[StandardName]
        List of Standard Names (ssno:standard_name)
    guidelines: Distribution
        Guidelines for the use of the Standard Name Table (dcat:Distribution)

    """
    standard_names: List[StandardName] = None  # ssno:standard_name
    guideline: Distribution = None  # ssno:guideline

    def __str__(self):
        return f'{self.title}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.title})'

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}(<a href={self.distribution.downloadURL}>{self.title}</a>)"

    @classmethod
    def parse(cls, filename, format='xml'):
        """Call the reader plugin for the given format"""
        Reader = plugins.get(format)
        xml_data: Dict = Reader(filename).parse()

        sndata = xml_data.pop('standard_name')
        for sn in sndata:
            if sn['description'] is None:
                name = sn['standard_name']
                warnings.warn(f'Description of "{name}" is None. Setting to empty string.')
                sn['description'] = ""
        return cls(title=str(filename),
                   standard_names=[StandardName(**sn) for sn in sndata],
                   **xml_data)
