import json
import os


class Config:

    def __init__(self):
        self.user_name: str = ""
        self.machine_name: str = ""
        self.orchestrator_url = ""
        self.bot_venv_path = ""
        self.bot_path = ""
        self.time_between_requests = 1

    def __str__(self):
        output_str = (f"user_name: {self.user_name}\t"
                      f"machine_name: {self.machine_name}\t"
                      f"orchestrator_url: {self.orchestrator_url}\t"
                      f"bot_venv_path: {self.bot_venv_path}\t"
                      f"bot_path: {self.bot_path}\t"
                      f"time_between_requests: {self.time_between_requests}")
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

        self.set_attributes_from_dict(json_main_dict)
