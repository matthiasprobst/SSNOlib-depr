import unittest

from rdflib import URIRef

from ssnolib.namespace import SSNO


class TestNamespace(unittest.TestCase):

    def test_namespace(self):
        self.assertIsInstance(SSNO.has_standard_names, URIRef)
        self.assertEqual(SSNO.has_standard_names, URIRef('https://matthiasprobst.github.io/ssno#has_standard_names'))
        self.assertEqual(SSNO.standard_name, URIRef('https://matthiasprobst.github.io/ssno#standard_name'))
