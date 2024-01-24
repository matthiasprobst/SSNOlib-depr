import pydantic
import warnings
from datetime import datetime
from typing import Union

from .core import Thing
from .namespace import QUDT_UNIT
from .resource import Dataset

qudt_canonical_unit_lookup = {
    's': QUDT_UNIT.SEC,  # time
    'm': QUDT_UNIT.M,  # length
    # derived units
    # velocity
    'm/s': QUDT_UNIT.M_PER_SEC,
    'm s-1': QUDT_UNIT.M_PER_SEC,
    'm*s-1': QUDT_UNIT.M_PER_SEC,
    'm*s^-1': QUDT_UNIT.M_PER_SEC,
    'm*s**-1': QUDT_UNIT.M_PER_SEC,
    # per length
    '1/m': QUDT_UNIT.PER_M,
    'm-1': QUDT_UNIT.PER_M,
    'm^-1': QUDT_UNIT.PER_M,
    'm**-1': QUDT_UNIT.PER_M,
    # per length squared
    '1/m2': QUDT_UNIT.PER_M2,
    '1/m**2': QUDT_UNIT.PER_M2,
    '1/m^2': QUDT_UNIT.PER_M2,
    'm-2': QUDT_UNIT.PER_M2,
    'm^-2': QUDT_UNIT.PER_M2,
    'm**-2': QUDT_UNIT.PER_M2,
    # per length cubed
    '1/m3': QUDT_UNIT.PER_M3,
    '1/m**3': QUDT_UNIT.PER_M3,
    '1/m^3': QUDT_UNIT.PER_M3,
    'm-3': QUDT_UNIT.PER_M3,
    'm^-3': QUDT_UNIT.PER_M3,
    'm**-3': QUDT_UNIT.PER_M3,
    # per second
    '1/s': QUDT_UNIT.PER_SEC,
    '1 s-1': QUDT_UNIT.PER_SEC,
    '1*s-1': QUDT_UNIT.PER_SEC,
    '1*s^-1': QUDT_UNIT.PER_SEC,
    '1*s**-1': QUDT_UNIT.PER_SEC,
    's-1': QUDT_UNIT.PER_SEC,
    's^-1': QUDT_UNIT.PER_SEC,
    's**-1': QUDT_UNIT.PER_SEC,
    # per second squared
    '1/s**2': QUDT_UNIT.PER_SEC2,
    '1/s^2': QUDT_UNIT.PER_SEC2,
    's^-2': QUDT_UNIT.PER_SEC2,
    's-2': QUDT_UNIT.PER_SEC2,
    's**-2': QUDT_UNIT.PER_SEC2,
    # frequency
    'Hz': QUDT_UNIT.HZ,
    # energy
    'joule': QUDT_UNIT.J,
    'Joule': QUDT_UNIT.J,
    'J': QUDT_UNIT.J,
    # power
    'W': QUDT_UNIT.W,
    'watt': QUDT_UNIT.W,
    'Watt': QUDT_UNIT.W,
    # pressure
    'Pa': QUDT_UNIT.PA,
    'pascal': QUDT_UNIT.PA,
    'Pascal': QUDT_UNIT.PA,
    # mass
    'kg': QUDT_UNIT.KiloGM,
    'kilogram': QUDT_UNIT.KiloGM,
    'kilograms': QUDT_UNIT.KiloGM,
    'Kilogram': QUDT_UNIT.KiloGM,
    'Kilograms': QUDT_UNIT.KiloGM,
    # temperature
    'K': QUDT_UNIT.K,
    'kelvin': QUDT_UNIT.K,
    'Kelvin': QUDT_UNIT.K,
    # volume
    'm3': QUDT_UNIT.M3,
    'm^3': QUDT_UNIT.M3,
    'm**3': QUDT_UNIT.M3,
    # torque
    'N m': QUDT_UNIT.N_M,
    'N*m': QUDT_UNIT.N_M
}


def parse_canonical_units(units):
    """Returns the IRI for a canonical units"""
    return str(qudt_canonical_unit_lookup.get(units, units))


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
