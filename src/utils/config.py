"""
A configuration parser for the Dataverse service. The configuration is expected to be in TOML
(https://toml.io/en/) format.
"""

from typing import Optional, BinaryIO, TextIO

import tomli

_SEC_SERVICE = "Service"
_SEC_SERVICE_DEPS = "Service_Dependencies"


class DataverseServiceConfig:
    """
    The dataverse service configuration parsed from a TOML configuration file. Once initialized,
    this class will contain the fields:

    service_root_path: str  | None - if the service is behind a reverse proxy that rewrites the
        service path, the path to the service. The path is required in order for the OpenAPI
        documentation to function.

    kbase_workspace_url: str - the URL of the KBase Workspace service.
    """

    def __init__(self, config_file: BinaryIO, service_root_path=None, kbase_workspace_url=None):
        """
        Create the configuration parser.
        config_file - an open file-like object, opened in binary mode, containing the TOML
            config file data.
        """
        if config_file:
            config = tomli.load(config_file)
            _check_missing_section(config, _SEC_SERVICE)
            _check_missing_section(config, _SEC_SERVICE_DEPS)

            self.service_root_path = _get_string_optional(config, _SEC_SERVICE, "root_path")
            self.kbase_workspace_url = _get_string_required(config, _SEC_SERVICE_DEPS, "kbase_workspace_url")
        else:
            self.service_root_path = service_root_path
            self.kbase_workspace_url = kbase_workspace_url

    def print_config(self, output: TextIO):
        """
        Print the configuration to the output argument, censoring secrets.
        """
        output.writelines([
            "\n*** Service Configuration ***\n",
            f"Service root path: {self.service_root_path}\n",
            f"Workspace URL: {self.kbase_workspace_url}\n",
            "*** End Service Configuration ***\n\n"
        ])


def _check_missing_section(config, section):
    if section not in config:
        raise ValueError(f"Missing section {section}")


# assumes section exists
def _get_string_required(config, section, key) -> str:
    putative = _get_string_optional(config, section, key)
    if not putative:
        raise ValueError(f"Missing value for key {key} in section {section}")
    return putative


# assumes section exists
def _get_string_optional(config, section, key) -> Optional[str]:
    putative = config[section].get(key)
    if putative is None:
        return None
    if type(putative) != str:
        raise ValueError(
            f"Expected string value for key {key} in section {section}, got {putative}")
    if not putative.strip():
        return None
    return putative.strip()


# assumes section exists
def _get_list_string(config, section, key) -> list:
    putative = _get_string_optional(config, section, key)
    if not putative:
        return []
    return [x.strip() for x in putative.split(",")]
