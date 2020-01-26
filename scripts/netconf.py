from nornir import InitNornir
from nornir.plugins.tasks.networking import netconf_get_config, netconf_edit_config
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from nornir.core.task import Result
from datetime import datetime
from pathlib import Path
from typing import Any, Union, Optional

from lxml import etree
from ruamel.yaml import YAML

nr = InitNornir(config_file="config.yaml")


yaml = YAML(typ="safe")

def save_nc_get_config(task):
    with open(f"nc-samples/get-config/{task.host.name}.xml", "w") as f:
        result = task.run(task=netconf_get_config, source="running")
        f.write(result.result)

def edit_nc_config_from_yaml(task, config_path: str):
    with open(config_path) as f:
        data = yaml.load(f)
        xml = dict_to_xml(data, root="config")
        xml_str = etree.tostring(xml).decode('utf-8')
        result = task.run(task=netconf_edit_config, config=xml_str)
        return Result(host=task.host, result=result.result)

def dict_to_xml(data: Any, root: Union[None, str, etree.Element] = None, attr_marker: str = '_') -> etree.Element:
    def _dict_to_xml(data_: Any, parent: Optional[etree.Element] = None) -> None:
        nonlocal root
        if not isinstance(data_, dict):
            raise ValueError("provided data must be a dictionary")

        for key, value in data_.items():
            if key.startswith(attr_marker):
                # handle keys starting with attr_marker as tag attributes
                attr_name = key.lstrip(attr_marker)
                parent.attrib[attr_name] = value
            else:
                element = etree.Element(key)
                if root is None:
                    root = element

                if parent is not None and not isinstance(value, list):
                    parent.append(element)

                if isinstance(value, dict):
                    _dict_to_xml(value, element)
                elif isinstance(value, list):
                    for item in value:
                        list_key = etree.Element(key)
                        parent.append(list_key)
                        _dict_to_xml(item, list_key)
                else:
                    if value is not None and not isinstance(value, str):
                        value = str(value)
                    element.text = value

    if isinstance(root, str):
        root = etree.Element(root)
    _dict_to_xml(data, root)
    return root


# results = nr.run(task=save_nc_get_config)
# print_result(results)

# r3 = nr.filter(F(name="R3"))
results = nr.run(task=edit_nc_config_from_yaml, config_path="acl.yaml")
print(results)