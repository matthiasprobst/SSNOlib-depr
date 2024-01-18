import abc
import pathlib
from typing import Dict, Union


class TableReader(abc.ABC):

    def __init__(self, filename: str):
        self.filename = filename

    @abc.abstractmethod
    def parse(self) -> Dict:
        """Parse the file"""


class XMLReader(TableReader):

    def __init__(self, filename: Union[str, pathlib.Path]):
        self.filename = pathlib.Path(filename)
        assert self.filename.exists(), f'{self.filename} does not exist'
        assert self.filename.is_file(), f'{self.filename} is not a file'

    def parse(self) -> Dict:
        """Parse the file"""
        try:
            import xmltodict
        except ImportError:
            raise ImportError('Package "xmltodict" is missing, but required to import from XML files.')

        with open(str(self.filename), 'r', encoding='utf-8') as file:
            my_xml = file.read()
        xmldict = xmltodict.parse(my_xml)
        _name = list(xmldict.keys())[0]

        xmldata = xmldict[_name]

        def _parse_standard_name(sndict):
            canonical_units = sndict.get('canonical units')
            description = sndict.get('description', )
            standard_name = sndict.get('@id')
            return dict(standard_name=standard_name,
                        canonical_units=canonical_units,
                        description=description)

        version = xmldata.get('version', None)
        if version is None:
            version = xmldata.get('version_number', None)

        last_modified = xmldata.get('last_modified', None)

        contact = xmldata.get('contact', None)
        if "@" in contact:
            # it is an email address
            contact = {'mbox': contact}
            # else cannot be parsed

        sn_data = xmldata.get('entry', None)
        if sn_data is None:
            raise KeyError('Expected key "entry" in the XML file.')
        return {'standard_name': [_parse_standard_name(sn) for sn in sn_data],
                'version': version,
                'last_modified': last_modified,
                'contact': contact}

        # for k in data.keys():
        #     if k not in ('entry', 'alias') and k[0] != '@':
        #         meta[k] = data[k]
        #
        # table = {}
        # for entry in data['entry']:
        #     table[entry.pop('@id')] = entry
        #
        # _alias = data.get('alias', {})
        #
        # if _alias:
        #     for aliasentry in _alias:
        #         k, v = list(aliasentry.values())
        #         table[v]['alias'] = k
        #
        # if 'version' not in meta:
        #     meta['version'] = f"v{meta.get('version_number', None)}"


_plugins = {
    'xml': XMLReader
}


def get(plugin_name: str) -> TableReader:
    """Returns the plugin"""
    plugin = _plugins.get(plugin_name, None)
    if plugin is None:
        raise KeyError(f'No plugin found for {plugin_name}')
    return plugin
