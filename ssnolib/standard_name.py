import json
import warnings
from typing import Union

import pydantic
import rdflib
from pydantic import HttpUrl

from .context import SSNO as SSNO_CONTEXT_URL
from .core import SSNOlibModel
from .resource import Dataset


class StandardName(SSNOlibModel):
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

    def dump_jsonld(self, id=None, context=SSNO_CONTEXT_URL) -> str:
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
        if context:
            return g.serialize(format='json-ld',
                               context={"@import": SSNO_CONTEXT_URL},
                               indent=4)
        return g.serialize(format='json-ld', indent=4)

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
