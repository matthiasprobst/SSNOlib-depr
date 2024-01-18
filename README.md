# SSNOlib

A Python library to work with the [sSNO ontology](https://matthiasprobst.github.io/ssno/).

## Installation

```bash
pip install git+https://github.com/matthiasprobst/SSNOlib.git
```

## Usage

Describe a Standard Name Table ith *sSNO*. Let's take the one from cfconventions.org as an example:

```python
import ssnolib

# Create a distribution object (downloadable XML file containing the standard name table)
distribution = ssnolib.Distribution(title='XML Table',
                                    downloadURL='http://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml',
                                    mediaType='application/xml')

# Create a standard name table object
snt = ssnolib.StandardNameTable(title='CF Standard Name Table v79',
                                distributions=[distribution, ])

# To describe this standard name table, we can export the JSON-LD file:
with open('cf79.jsonld', 'w', encoding='utf-8') as f:
    f.write(snt.dump_jsonld())
```

The corresponding JSON-LD file looks like this (showing only 2 standard names for shortness):

```json
{
  "@context": {
    "@import": "https://raw.githubusercontent.com/matthiasprobst/ssno/main/ssno_context.jsonld"
  },
  "@graph": [
    {
      "@id": "_:",
      "@type": "StandardNameTable",
      "title": "CF Standard Name Table 83",
      "version": "83",
      "has_standard_names": [
        {
          "@id": "_:acoustic_area_backscattering_strength_in_sea_water"
        },
        {
          "@id": "_:acoustic_signal_roundtrip_travel_time_in_sea_water"
        }
      ],
      "https://matthiasprobst.github.io/ssno#contact": {
        "@id": "_:contact"
      }
    },
    {
      "@id": "_:contact",
      "@type": "Person",
      "mbox": "support@ceda.ac.uk"
    },
    {
      "@id": "_:acoustic_area_backscattering_strength_in_sea_water",
      "@type": "StandardName",
      "canonical_units": "",
      "description": "Acoustic area backscattering strength is 10 times the log10 of the ratio of the area backscattering coefficient to the reference value, 1 (m2 m-2). Area backscattering coefficient is the integral of the volume backscattering coefficient over a defined distance. Volume backscattering coefficient is the linear form of acoustic_volume_backscattering_strength_in_sea_water. For further details see MacLennan et. al (2002) doi:10.1006/jmsc.2001.1158.",
      "standard_name": "acoustic_area_backscattering_strength_in_sea_water"
    },
    {
      "@id": "_:acoustic_signal_roundtrip_travel_time_in_sea_water",
      "@type": "StandardName",
      "canonical_units": "",
      "description": "The quantity with standard name acoustic_signal_roundtrip_travel_time_in_sea_water is the time taken for an acoustic signal to propagate from the emitting instrument to a reflecting surface and back again to the instrument. In the case of an instrument based on the sea floor and measuring the roundtrip time to the sea surface, the data are commonly used as a measure of ocean heat content.",
      "standard_name": "acoustic_signal_roundtrip_travel_time_in_sea_water"
    }
  ]
}
```

### Standard name to JSON-LD

```python
import ssnolib

air_temp = ssnolib.StandardName(standard_name='air_temperature',
                                canonical_units='K',
                                description='Air temperature is the bulk temperature of the air, not the surface (skin) temperature.',
                                dbpedia_match='http://dbpedia.org/resource/Air_temperature')

# write to JSON-LD
with open('air_temperature.json', 'w') as f:
    f.write(air_temp)
```

The corresponding JSON-LD file looks like this:

```json
{
  "@context": {
    "@import": "https://raw.githubusercontent.com/matthiasprobst/ssno/main/ssno_context.jsonld"
  },
  "@id": "_:",
  "@type": "StandardName",
  "canonical units": "https://qudt.org/vocab/unit/K",
  "dbpedia match": "http://dbpedia.org/resource/Air_temperature",
  "description": "Air temperature is the bulk temperature of the air, not the surface (skin) temperature.",
  "standard name": "air_temperature"
}
```

You can now take the JSON-LD file and use it with your data (place it next to it, upload it to a server, etc.).
