"""Test parse object_store_conf.xml."""

from pathlib import Path
import galaxy_jwd
from pprint import pprint

OBJECT_STORE_YML = str(Path(__file__).parent / 'test_object_store_conf.yml')
OBJECT_STORE_XML = str(Path(__file__).parent / 'test_object_store_conf.xml')

yaml_conf = galaxy_jwd.parse_object_store(OBJECT_STORE_YML)
xml_conf = galaxy_jwd.parse_object_store(OBJECT_STORE_XML)

print("Read XML config:")
pprint(xml_conf)
print("\nRead YAML config:")
pprint(yaml_conf)
