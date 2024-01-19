import json
import pathlib
import unittest
import warnings

import pydantic
import rdflib

import ssnolib
from ssnolib.context import SSNO as SSNO_CONTEXT_URL

__this_dir__ = pathlib.Path(__file__).parent
CACHE_DIR = ssnolib.utils.get_cache_dir()


def _delete_test_data():
    for _filename_to_delete in (CACHE_DIR / 'cf-standard-name-table.xml',
                                CACHE_DIR / 'cfsnt.json',
                                CACHE_DIR / 'cf_table.json',
                                CACHE_DIR / 'cfsnt.json',
                                CACHE_DIR / 'test_snt.yaml',
                                CACHE_DIR / 'cf-standard-name-table.xml',):
        _filename_to_delete.unlink(missing_ok=True)


class TestClasses(unittest.TestCase):

    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=UserWarning)
        _delete_test_data()

    def tearDown(self) -> None:
        _delete_test_data()

    def test_Person(self):
        contact = ssnolib.Person(mbox='johndoe@email.com')
        self.assertEqual(str(contact.mbox), 'johndoe@email.com')

        contact = ssnolib.Person(first_name='John', last_name='Doe')
        self.assertEqual(contact.first_name, 'John')
        self.assertEqual(contact.last_name, 'Doe')

    def test_ssnolib_Distribution(self):
        distribution = ssnolib.Distribution(title='XML Table',
                                            download_URL='http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml',
                                            media_type='text/csv')
        self.assertEqual(str(distribution.media_type),
                         "https://www.iana.org/assignments/media-types/text/csv")

        distribution = ssnolib.Distribution(title='XML Table',
                                            download_URL='http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml',
                                            media_type='application/xml')
        self.assertEqual(str(distribution.media_type),
                         "https://www.iana.org/assignments/media-types/application/xml")
        self.assertEqual(distribution.title, 'XML Table')
        self.assertEqual(str(distribution.download_URL),
                         'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml')

        download_filename = distribution.download('cf-standard-name-table.xml')
        self.assertIsInstance(download_filename, pathlib.Path)
        self.assertTrue(download_filename.exists())
        self.assertTrue(download_filename.is_file())
        download_filename.unlink(missing_ok=True)

    def test_standard_name_table(self):
        snt = ssnolib.StandardNameTable(title='CF Standard Name Table v79')
        self.assertEqual(snt.title, 'CF Standard Name Table v79')
        self.assertEqual(str(snt), 'CF Standard Name Table v79')
        self.assertEqual(repr(snt), 'StandardNameTable(title=CF Standard Name Table v79)')

        distribution = ssnolib.Distribution(title='XML Table',
                                            download_URL='http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml',
                                            media_type='application/xml')
        self.assertEqual(distribution.title, 'XML Table')
        self.assertEqual(str(distribution.download_URL),
                         'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml')
        snt = ssnolib.StandardNameTable(title='CF Standard Name Table v79',
                                        distribution=[distribution, ])
        self.assertEqual(snt.distribution[0].title, 'XML Table')
        self.assertEqual(str(snt.distribution[0].download_URL),
                         'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml')
        table_filename = snt.distribution[0].download(
            dest_filename=CACHE_DIR / 'cf-standard-name-table.xml',
        )
        self.assertIsInstance(table_filename, pathlib.Path)
        self.assertTrue(table_filename.exists())
        self.assertTrue(table_filename.is_file())
        self.assertEqual(table_filename, CACHE_DIR / 'cf-standard-name-table.xml')
        try:
            snt.distribution[0].download(
                dest_filename=CACHE_DIR / 'cf-standard-name-table.xml',
            )
        except FileExistsError:
            pass
        snt.distribution[0].download(
            dest_filename=CACHE_DIR / 'cf-standard-name-table.xml',
            overwrite_existing=True
        )
        snt_from_xml = snt.parse(table_filename, format='xml')
        self.assertIsInstance(snt_from_xml.standard_names, list)
        for sn in snt_from_xml.standard_names:
            self.assertIsInstance(sn, ssnolib.StandardName)

        snt_from_xml_dict = snt_from_xml.model_dump(exclude_none=True)
        self.assertDictEqual(snt_from_xml_dict['contact'],
                             {'mbox': 'support@ceda.ac.uk'})

        with self.assertRaises(pydantic.ValidationError):
            # invalid string for title:
            ssnolib.StandardNameTable(title=123)

        snt_from_xml.title = f'CF Standard Name Table {snt_from_xml.version}'
        with open(CACHE_DIR / 'cfsnt.json', 'w', encoding='utf-8') as f:
            f.write(snt_from_xml.dump_jsonld())

        g = rdflib.Graph().parse(CACHE_DIR / 'cfsnt.json', format='json-ld')
        for s, p, o in g.triples((None, None, None)):
            self.assertIsInstance(p, rdflib.URIRef)

    def test_standard_name(self):
        """describe "air_temperature" from
        http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html"""

        with self.assertRaises(pydantic.ValidationError):
            # invalid canonical_units
            ssnolib.StandardName(
                standard_name='air_temperature',
                canonical_units=123,
                description='Air temperature is the bulk temperature of the air, not the surface (skin) temperature.', )

        atemp = ssnolib.StandardName(
            standard_name='air_temperature',
            canonical_units='K',
            description='Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')

        self.assertEqual(str(atemp), 'air_temperature')
        self.assertEqual(atemp.standard_name, 'air_temperature')
        self.assertEqual(atemp.canonical_units, 'K')
        self.assertEqual(atemp.description,
                         'Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')

        self.assertEqual(str(atemp), 'air_temperature')
        self.assertEqual(atemp.standard_name_table, None)

        # to dict:
        atemp_dict = atemp.model_dump(exclude_none=True)
        self.assertIsInstance(atemp_dict, dict)
        self.assertEqual(atemp_dict['standard_name'], 'air_temperature')
        self.assertEqual(atemp_dict['canonical_units'], 'K')
        self.assertEqual(atemp_dict['description'],
                         'Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')

        atemp_json = atemp.model_dump_json()
        self.assertIsInstance(atemp_json, str)
        atemp_json_dict = json.loads(atemp_json)
        self.assertIsInstance(atemp_json_dict, dict)
        self.assertEqual(atemp_json_dict['standard_name'], 'air_temperature')
        self.assertEqual(atemp_json_dict['canonical_units'], 'K')
        self.assertEqual(atemp_json_dict['description'],
                         'Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')

        # to json-ld:
        atemp_jsonld = atemp.dump_jsonld()

        with open(CACHE_DIR / 'cf_table.json', 'w') as f:
            f.write(atemp_jsonld)

        g = rdflib.Graph()
        g.parse(data=atemp_jsonld, format='json-ld')
        self.assertEqual(len(g), 4)
        for s, p, o in g:
            self.assertIsInstance(s, rdflib.URIRef)
            self.assertIsInstance(p, rdflib.URIRef)
            self.assertIsInstance(o, str)

        # serialize with rdflib:
        jsonld_dict = json.loads(atemp_jsonld)
        self.assertEqual(jsonld_dict['@context']['@import'], SSNO_CONTEXT_URL)

        self.assertEqual(jsonld_dict['@type'], 'StandardName')
        self.assertEqual(jsonld_dict['standard name'], 'air_temperature')
        self.assertEqual(jsonld_dict['canonical units'], 'https://qudt.org/vocab/unit/K')

        # https://qudt.org/vocab/unit/K

    def test_snt_from_yaml(self):
        snt_yml_filename = __this_dir__ / 'data/test_snt.yaml'
        distribution = ssnolib.Distribution(title='XML Table',
                                            download_URL=f'file:///{snt_yml_filename}',
                                            media_type='application/yaml')
        filename = distribution.download(CACHE_DIR / 'test_snt.yaml')
        self.assertNotEqual(filename, snt_yml_filename)
        self.assertTrue(pathlib.Path(filename).exists())
        self.assertIsInstance(filename, pathlib.Path)
        snt = ssnolib.StandardNameTable(
            title='Yaml Test SNT',
            distribution=[distribution]
        )
        snt.parse(snt.distribution[0])
