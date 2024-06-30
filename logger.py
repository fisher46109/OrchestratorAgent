import os
from datetime import datetime


class Logger:
    """ Class of handling logs """

    def __init__(self):
        self.logs_folder_path = f"{os.path.dirname(__file__)}\\logs"
        if not os.path.exists(self.logs_folder_path):
            try:
                os.mkdir(self.logs_folder_path)
            except Exception as e:
                raise e

    def log(self, message: str = ""):

        act_time = datetime.now()
        log_time = act_time.strftime('%Y-%m-%d %H:%M:%S')
        log_time_to_name = act_time.strftime('%Y-%m-%d')
        file_name = f"AgentLog_{log_time_to_name}.txt"
        file_path = os.path.join(self.logs_folder_path, file_name)

        with open(file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f'{log_time};{message}\n')

    def remove_old_logs(self):  # TODO write code
        pass
