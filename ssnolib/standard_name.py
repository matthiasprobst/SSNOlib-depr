import pydantic
import warnings
from datetime import datetime
from typing import Union

from .core import Thing
from .resource import Dataset
from .namespace import QUDT_UNIT

qudt_unit_lookup = {
    's': QUDT_UNIT.SEC,
    'm': QUDT_UNIT.M,
    'cm': QUDT_UNIT.CentiM,
    'mm': QUDT_UNIT.MilliM,
    'um': QUDT_UNIT.MicroM,
    'nm': QUDT_UNIT.NanoM,
    'pm': QUDT_UNIT.PicoM,
    'fm': QUDT_UNIT.FemtoM,
    'hz': QUDT_UNIT.HZ,
    'KHz': QUDT_UNIT.KiloHZ,
    'kHz': QUDT_UNIT.KiloHZ,
    'MHz': QUDT_UNIT.MegaHZ,
    'GHz': QUDT_UNIT.GigaHZ,
    'THz': QUDT_UNIT.TeraHZ,
    'joule': QUDT_UNIT.J,
    'Joule': QUDT_UNIT.J,
    'J': QUDT_UNIT.J,
    'mJ': QUDT_UNIT.MilliJ,
    'uJ': QUDT_UNIT.MicroJ,
    'kJ': QUDT_UNIT.KiloJ,
    'MJ': QUDT_UNIT.MegaJ,
    'GJ': QUDT_UNIT.GigaJ,
    'K': QUDT_UNIT.K,
    'N m': QUDT_UNIT.N_M
}


def parse_canonical_units(units):
    """Returns the IRI for a canonical units"""
    return str(qudt_unit_lookup.get(units, units))


class StandardName(Thing):
    """Implementation of ssno:StandardNmae"""
    standard_name: str
    canonical_units: Union[str, None]
    description: str  # dcterms:description
    standard_name_table: Dataset = None  # ssno:standard_name_table (subclass of dcat:Dataset)

    class JSONLDSerializer:
        def __call__(self, key, value):
            if key == 'canonical units':
                return parse_canonical_units(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

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
        """Validates the download_URL field"""
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

    # def dump_jsonld(self, id=None, context=SSNO_CONTEXT_URL) -> str:
    #     """alias for model_dump_json()"""
    #
    #     g = rdflib.Graph()
    #     _atemp_json_dict = {k.replace('_', ' '): v for k, v in self.model_dump().items()}
    #
    #     _qudt_unit_dict = {"K": "https://qudt.org/vocab/unit/K"}
    #
    #     _atemp_json_dict['canonical units'] = _qudt_unit_dict.get(_atemp_json_dict['canonical units'],
    #                                                               _atemp_json_dict['canonical units'])
    #
    #     _id = '_:' or id
    #     jsonld = {"@context": {"@import": context},
    #               "@graph": [
    #                   {"@id": _id,
    #                    "@type": "ssno:StandardName",
    #                    **_atemp_json_dict}
    #               ]}
    #
    #     g.parse(data=json.dumps(jsonld), format='json-ld')
    #     if context:
    #         return g.serialize(format='json-ld',
    #                            context={"@import": context},
    #                            indent=4)
    #     return g.serialize(format='json-ld', indent=4)

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return self.standard_name
