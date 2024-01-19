import json
import pathlib
from datetime import datetime
from typing import List, Union, Dict

import rdflib

from . import plugins
from .context import SSNO as SSNO_CONTEXT_URL
from .namespace import SSNO
from .resource import Dataset, Distribution
from .standard_name import StandardName


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

    """
    standard_names: List[StandardName] = None  # ssno:standard_name

    def __str__(self):
        return f'{self.title}'

    def _repr_html_(self):
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}(<a href={self.distribution.downloadURL}>{self.title}</a>)"

    @classmethod
    def parse(cls,
              source: Union[str, pathlib.Path, Distribution],
              format=None):
        """Call the reader plugin for the given format.
        Format will select the reader plugin to use. Currently 'xml' is supported."""
        if isinstance(source, (str, pathlib.Path)):
            filename = source
            if format is None:
                filename = source
                format = pathlib.Path(source).suffix[1:].lower()
                if format not in plugins:
                    raise ValueError(
                        f'No plugin found for the file. The reader was determined based on the suffix: {format}. '
                        'You may overwrite this by providing the parameter format'
                    )
        else:
            if format is None:
                format = source.mediaType
            filename = source.download()

        Reader = plugins.get(format)
        data: Dict = Reader(filename).parse()

        return cls(**data)

    def dump_jsonld(self, context=SSNO_CONTEXT_URL) -> str:
        """Returns the JSON-LD representation of the class"""
        _id = '_:' or id
        jsonld = {"@context": {"@import": SSNO_CONTEXT_URL},
                  "@graph": [
                      {"@id": _id,
                       "@type": str(SSNO.StandardNameTable),
                       "title": self.title}
                  ]}
        if self.description:
            jsonld['@graph'][0]['description'] = self.description
        if self.contact:
            contact = {'@id': '_:contact',
                       '@type': 'Person',
                       **self.contact.model_dump(exclude_none=True)}
            # if 'first_name'
            jsonld['@graph'][0]['contact'] = contact
        if self.modified:
            jsonld['@graph'][0]['modified'] = str(self.modified)
        if self.version:
            jsonld['@graph'][0]['version'] = self.version
        if self.identifier:
            jsonld['@graph'][0]['identifier'] = str(self.identifier)
        if self.standard_names:
            sn_type = str(SSNO.StandardName)
            jsonld['@graph'][0]['standard names'] = []
            for sn in self.standard_names[0:2]:
                jsonld['@graph'][0]['standard names'].append({'@id': f'_:{sn.standard_name}',
                                                              '@type': sn_type,
                                                              **sn.model_dump(exclude_none=True)})
        g = rdflib.Graph()
        g.parse(data=json.dumps(jsonld), format='json-ld')
        if context:
            return g.serialize(format='json-ld',
                               context={"@import": SSNO_CONTEXT_URL},
                               indent=4)
        return g.serialize(format='json-ld', indent=4)
