from typing import Dict

from ruamel.yaml import YAML

import constants
from constants import (
    NORMALIZED_INTERFACES,
    INTERFACE_NAME_RE,
    NEIGHBOR_SPLIT_RE,
    CDP_NEIGHBOR_RE,
    HOSTS_FILE,
    DEVICE_USERNAME,
    DEVICE_PASSWORD,
    DEVICE_TYPE,
    CONNECTION_TIMEOUT,
)


def normalize_interface_type(interface_type: str) -> str:
    """Normalizes interface type

    For example, G is converted to GigabitEthernet, Te is converted to TenGigabitEthernet
    """
    int_type = interface_type.strip().lower()
    for norm_int_type in NORMALIZED_INTERFACES:
        if norm_int_type.lower().startswith(int_type):
            return norm_int_type
    return int_type


def normalize_interface_name(interface_name: str) -> str:
    """Normalizes interface name
    
    For example, Gi0/1 is converted to GigabitEthernet1,
    Te1/1 is converted to TenGigabitEthernet1/1
    """
    match = INTERFACE_NAME_RE.search(interface_name)
    if match:
        int_type = match.group("interface_type")
        normalized_int_type = normalize_interface_type(int_type)
        int_num = match.group("interface_num")
        return normalized_int_type + int_num
    raise ValueError(f"Does not recognize {interface_name} as an interface name")


def extract_hostname_from_fqdn(fqdn: str) -> str:
    """Extracts hostname from fqdn-like string
    
    For example, R1.cisco.com -> R1,  sw1 -> sw1"
    """
    return fqdn.split(".")[0]


def parse_show_cdp_neighbors(cli_output: str) -> Dict[str, Dict[str, str]]:
    """Parses `show cdp neighbors` and returns a dictionary of neighbors and connected interfaces"""
    result: Dict[str, Dict[str, str]] = {}
    for neighbor_output in NEIGHBOR_SPLIT_RE.split(cli_output):
        match = CDP_NEIGHBOR_RE.search(neighbor_output)
        if match:
            remote_fqdn = match.group("remote_fqdn")
            local_interface = normalize_interface_name(match.group("local_interface"))
            remote_interface = normalize_interface_name(match.group("remote_interface"))
            remote_hostname = extract_hostname_from_fqdn(remote_fqdn)
            result[local_interface] = {
                "connected_device": {
                    "name": remote_hostname,
                    "port": remote_interface,
                }
            }
    return dict(sorted(result.items()))


def get_devices_conn_params() -> Dict[str, Dict[str, str]]:
    """Creates a dictionary of connection parameters for SSH"""
    result: Dict[str, Dict[str, str]] = {}
    yaml = YAML()
    with open(HOSTS_FILE, 'r') as f:
        hosts = yaml.load(f)
    for device, device_details in hosts["devices"]["routers"].items():
        device_params = {
            "host": device_details["host"],
            "username": DEVICE_USERNAME,
            "password": DEVICE_PASSWORD,
            "device_type": DEVICE_TYPE,
            "timeout": CONNECTION_TIMEOUT,
            "global_delay_factor": constants.NETMIKO_GLOBAL_DELAY_FACTOR,
        }
        result[device] = device_params
    return result
