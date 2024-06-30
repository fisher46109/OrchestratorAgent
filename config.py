import json
import os


class Config:

    def __init__(self):
        self.user_name: str = ""
        self.machine_name: str = ""
        self.orchestrator_url: str = ""
        self.bot_venv_path: str = ""
        self.bot_path: str = ""
        self.temp_path: str = ""
        self.time_between_requests: int = 1
        self.max_download_bot_retries: int = 0
        self.time_to_next_download_try: int = 0
        self.time_if_connection_error: int = 0

    def __str__(self):
        output_str = (f"user_name: {self.user_name}\t"
                      f"machine_name: {self.machine_name}\t"
                      f"orchestrator_url: {self.orchestrator_url}\t"
                      f"bot_venv_path: {self.bot_venv_path}\t"
                      f"bot_path: {self.bot_path}\t"
                      f"temp_path: {self.temp_path}\t"
                      f"time_between_requests: {self.time_between_requests}\t"
                      f"max_download_bot_retries: {self.max_download_bot_retries}\t"
                      f"time_to_next_download_try: {self.time_to_next_download_try}\t"
                      f"time_if_connection_error: {self.time_if_connection_error}\t")
        return output_str

    def set_attributes_from_dict(self, conf_dict: dict):
        """ Assignment keys from JSON to object attributes (if present in attributes list) """

        for key, value in conf_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def load_config(self):
        """ Load config from environment and config.json and assign all to Config attributes"""

        self.user_name = os.environ.get('USERNAME')
        self.machine_name = os.environ.get('COMPUTERNAME')

        config_path: str = f"{os.path.dirname(__file__)}\\config.json"
        with open(config_path, 'r', encoding='utf-8') as json_file:
            json_main_dict = json.load(json_file)

        self.replace_keywords(json_main_dict, "{username}", self.user_name)
        self.set_attributes_from_dict(json_main_dict)

    @staticmethod
    def replace_keywords(processed_dict: dict, old_string: str, new_string: str):
        """ Static method to convert keywords contained in configuration files """

        for key, value in processed_dict.items():
            if isinstance(value, str):
                if old_string in value:
                    processed_dict[key] = value.replace(old_string, new_string)

