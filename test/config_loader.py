from typing import Optional, BinaryIO, TextIO

import tomli

_SEC_SERVICE = "Service"
_SEC_SERVICE_DEPS = "Service_Dependencies"


class Config:
    def __init__(self, config_file: BinaryIO):
        """
        Create the configuration parser.
        config_file - an open file-like object, opened in binary mode, containing the TOML
            config file data.
        """
        if not config_file:
            raise ValueError("config_file is required")
        self.config = tomli.load(config_file)
        _check_missing_section(self.config, _SEC_SERVICE_DEPS)
        self.kbase_workspace_url = _get_string_required(self.config, _SEC_SERVICE_DEPS, "kbase_workspace_url")
        self.kbase_auth_token = _get_string_required(self.config, _SEC_SERVICE_DEPS, "kbase_auth_token")

    def print_config(self, output: TextIO):
        """
        Print the configuration to the output argument, censoring secrets.
        """
        output.writelines([
            "\n*** Service Configuration ***\n",
            f"Workspace URL: {self.kbase_workspace_url}\n",
            f"KBase Auth token: {self.kbase_auth_token}\n",
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
def _get_list_string(config, section, key) -> list[str]:
    putative = _get_string_optional(config, section, key)
    if not putative:
        return []
    return [x.strip() for x in putative.split(",")]
