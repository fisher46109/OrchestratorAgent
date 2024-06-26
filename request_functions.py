import requests


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

    def update_all(self, ssk_flag: str = "", state: str = "", result: str = "", robot_update_flag: str = ""):
        dict_to_send = {Keys.SSK_FLAG: ssk_flag,
                        Keys.STATE: state,
                        Keys.RESULT: result,
                        Keys.ROBOT_UPDATE_FLAG: robot_update_flag
                        }
        url = f'{self.main_url}/api/update_info/{self.query_url}'
        response = requests.patch(url, json=dict_to_send)
        response.raise_for_status()  # raise exception if response not ok


class Keys:
    """ Constant values to store key names in dictionary corresponding to model in server """

    STATE: str = "state"
    RESULT: str = "result"
    SSK_FLAG: str = "ssk_flag"
    ROBOT_UPDATE_FLAG: str = "robot_update_flag"


class SskState:
    """ Constant values to store instructions in ssk_flag"""

    START: str = "START"
    STOP: str = "STOP"
    KILL: str = "KILL"
    IDLE: str = "-"


class StateState:
    """ Constant values to store instructions in resultRe"""

    ACTIVE: str = "ACTIVE"
    STOPPED: str = "STOPPED"
    STOPPING: str = "STOPPING"
    KILLED: str = "KILLED"
    IDLE: str = "-"
