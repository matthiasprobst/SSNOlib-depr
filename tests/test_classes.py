import json
import pathlib
import unittest

import pydantic

from ssnolib import StandardName, StandardNameTable, Contact, Distribution
from ssnolib.context import SSNO as SSNO_CONTEXT_URL

__this_dir__ = pathlib.Path(__file__).parent


def _delete_test_data():
    _filename_to_delete = __this_dir__ / 'cf-standard-name-table.xml'
    _filename_to_delete.unlink(missing_ok=True)


class TestClasses(unittest.TestCase):

    def setUp(self) -> None:
        _delete_test_data()

    def tearDown(self) -> None:
        _delete_test_data()

    def test_Contact(self):
        contact = Contact(mbox='johndoe@email.com')
        self.assertEqual(str(contact.mbox), 'johndoe@email.com')

        contact = Contact(first_name='John', last_name='Doe')
        self.assertEqual(contact.first_name, 'John')
        self.assertEqual(contact.last_name, 'Doe')

    def test_Distribution(self):
        distribution = Distribution(title='XML Table',
                                    downloadURL='http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml',
                                    mediaType='application/xml')
        self.assertEqual(distribution.title, 'XML Table')
        self.assertEqual(distribution.downloadURL,
                         'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml')
        self.assertEqual(distribution.mediaType, 'application/xml')

        download_filename = distribution.download('cf-standard-name-table.xml')
        self.assertIsInstance(download_filename, pathlib.Path)
        self.assertTrue(download_filename.exists())
        self.assertTrue(download_filename.is_file())
        download_filename.unlink(missing_ok=True)

    def test_standard_name_table(self):
        snt = StandardNameTable(title='CF Standard Name Table v79')
        self.assertEqual(snt.title, 'CF Standard Name Table v79')
        self.assertEqual(str(snt), 'CF Standard Name Table v79')
        self.assertEqual(repr(snt), 'StandardNameTable(CF Standard Name Table v79)')

        distribution = Distribution(title='XML Table',
                                    downloadURL='http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml',
                                    mediaType='application/xml')
        self.assertEqual(distribution.title, 'XML Table')
        self.assertEqual(distribution.downloadURL,
                         'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml')
        snt = StandardNameTable(title='CF Standard Name Table v79',
                                distribution=[distribution, ])
        self.assertEqual(snt.distribution[0].title, 'XML Table')
        self.assertEqual(snt.distribution[0].downloadURL,
                         'http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml')
        table_filename = snt.distribution[0].download(
            dest_filename=__this_dir__ / 'cf-standard-name-table.xml',
        )
        self.assertIsInstance(table_filename, pathlib.Path)
        self.assertTrue(table_filename.exists())
        self.assertTrue(table_filename.is_file())
        self.assertEqual(table_filename, __this_dir__ / 'cf-standard-name-table.xml')
        try:
            snt.distribution[0].download(
                dest_filename=__this_dir__ / 'cf-standard-name-table.xml',
            )
        except FileExistsError:
            pass
        snt.distribution[0].download(
            dest_filename=__this_dir__ / 'cf-standard-name-table.xml',
            overwrite_existing=True
        )
        snt_from_xml = snt.parse(table_filename, format='xml')
        self.assertIsInstance(snt_from_xml.standard_names, list)
        for sn in snt_from_xml.standard_names:
            self.assertIsInstance(sn, StandardName)

        snt_from_xml_dict = snt_from_xml.model_dump(exclude_none=True)
        self.assertDictEqual(snt_from_xml_dict['contact'],
                             {'mbox': 'support@ceda.ac.uk'})

        with self.assertRaises(pydantic.ValidationError):
            # invalid string for title:
            StandardNameTable(title=123)

    def test_standard_name(self):
        """describe "air_temperature" from
        http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html"""

        with self.assertRaises(pydantic.ValidationError):
            # invalid URL
            StandardName(standard_name='air_temperature',
                         canonical_units='K',
                         description='Air temperature is the bulk temperature of the air, not the surface (skin) temperature.',
                         dbpedia_match='Air_temperature')

        atemp = StandardName(standard_name='air_temperature',
                             canonical_units='K',
                             description='Air temperature is the bulk temperature of the air, not the surface (skin) temperature.',
                             dbpedia_match='http://dbpedia.org/resource/Air_temperature')

        self.assertEqual(str(atemp), 'air_temperature')
        self.assertEqual(atemp.standard_name, 'air_temperature')
        self.assertEqual(atemp.canonical_units, 'K')
        self.assertEqual(atemp.description,
                         'Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')
        self.assertEqual(atemp.dbpedia_match, 'http://dbpedia.org/resource/Air_temperature')

        self.assertEqual(str(atemp), 'air_temperature')
        self.assertEqual(atemp.standard_name_table, None)

        # to dict:
        atemp_dict = atemp.model_dump(exclude_none=True)
        self.assertIsInstance(atemp_dict, dict)
        self.assertEqual(atemp_dict['standard_name'], 'air_temperature')
        self.assertEqual(atemp_dict['canonical_units'], 'K')
        self.assertEqual(atemp_dict['description'],
                         'Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')
        self.assertEqual(atemp_dict['dbpedia_match'], 'http://dbpedia.org/resource/Air_temperature')

        atemp_json = atemp.model_dump_json()
        self.assertIsInstance(atemp_json, str)
        atemp_json_dict = json.loads(atemp_json)
        self.assertIsInstance(atemp_json_dict, dict)
        self.assertEqual(atemp_json_dict['standard_name'], 'air_temperature')
        self.assertEqual(atemp_json_dict['canonical_units'], 'K')
        self.assertEqual(atemp_json_dict['description'],
                         'Air temperature is the bulk temperature of the air, not the surface (skin) temperature.')
        self.assertEqual(atemp_json_dict['dbpedia_match'], 'http://dbpedia.org/resource/Air_temperature')

        # to json-ld:
        atemp_jsonld = atemp.dump_jsonld()

        # serialize with rdflib:
        jsonld_dict = json.loads(atemp_jsonld)
        self.assertEqual(jsonld_dict['@context']['@import'], SSNO_CONTEXT_URL)

        self.assertEqual(jsonld_dict['@type'], 'StandardName')
        self.assertEqual(jsonld_dict['standard name'], 'air_temperature')
        self.assertEqual(jsonld_dict['canonical units'], 'https://qudt.org/vocab/unit/K')

        # https://qudt.org/vocab/unit/K
