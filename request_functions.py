import os
import requests
import app


class RequestFunctions:

    def __init__(self, main_url: str, user_name: str, machine_name: str):
        """ Init with data specified for agent """

        self.main_url = main_url
        self.user = user_name
        self.machine = machine_name
        self.query_url = f'?user={self.user}&machine={self.machine}'

    def get_info(self) -> dict:
        """ Get control info from orchestrator """

        url = f'{self.main_url}/api/get_object/{self.query_url}'
        response = requests.get(url)
        response.raise_for_status()  # raise exception if response not ok

        data: dict = response.json()

        return data

    def update_all(self):
        """ Update all control values  """

        dict_to_send = {Keys.SSK_FLAG: app.bot.ssk_flag,
                        Keys.STATE: app.bot.state,
                        Keys.RESULT: app.bot.result,
                        Keys.ROBOT_UPDATE_FLAG: app.bot.robot_update_flag
                        }
        url = f'{self.main_url}/api/update_info/{self.query_url}'
        response = requests.patch(url, json=dict_to_send)
        response.raise_for_status()  # raise exception if response not ok

    def download_robot(self, robot_name) -> str:
        """ - Download .zip to temp folder (create it if not exist) """

        file_path = ""

        temp_bot_path = app.config.temp_path
        if not os.path.exists(temp_bot_path):
            os.mkdir(temp_bot_path)

        url = f'{self.main_url}/send_robot_to_agent/{robot_name}'
        # request wit requirement of partial response
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Get filename from header value in 'Content-Disposition'
        filename = response.headers.get('Content-Disposition').split("zip_files/")[1][:-1]
        file_path = f"{temp_bot_path}\\{filename}"

        # open file to write data in write-binary mode
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        return file_path


class Keys:
    """ Constant values to store key names in dictionary corresponding to model in server """

    STATE: str = "state"
    RESULT: str = "result"
    SSK_FLAG: str = "ssk_flag"
    ROBOT_UPDATE_FLAG: str = "robot_update_flag"
    ROBOT_NAME: str = "robot"


class SskState:
    """ Constant values to store instructions in ssk_flag"""

    START: str = "START"
    STOP: str = "STOP"
    KILL: str = "KILL"
    IDLE: str = "-"


class StateState:
    """ Constant values to store instructions in state"""

    ACTIVE: str = "ACTIVE"
    STOPPED: str = "STOPPED"
    STOPPING: str = "STOPPING"
    KILLED: str = "KILLED"
    IDLE: str = "-"


class RobotUpdateFlag:
    """ Constant values to store instructions in robot_update_flag"""

    UPDATE: str = "UPDATE"
    IDLE: str = "-"
