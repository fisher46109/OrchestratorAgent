import os
import shutil
import subprocess
import threading
import zipfile
from custom_exceptions import UpdateException
from request_functions import StateState, SskState, RobotUpdateFlag, Keys
import app


class BotHandler:
    """ Class to handle all operations with bot (subprocess) """

    def __init__(self):
        self.ssk_flag = SskState.IDLE
        self.running = False
        self.state = StateState.IDLE
        self.result = "-"
        self.robot_name = ""
        self.robot_update_flag = RobotUpdateFlag.IDLE
        # None initialization of subprocess (bot)
        self.bot: subprocess.Popen | None = None
        # None initialization of background thread to read info from subprocess (bot)
        self.input_thread: threading.Thread | None = None

    def __str__(self):
        return (f"ssk_flag: {self.ssk_flag}\t"
                f"Running: {self.running}\t"
                f"State: {self.state}\t"
                f"Result: {self.result}\t"
                f"robot_update_flag: {self.robot_update_flag}\t")

    def set_control_values(self, values_dict: dict):
        """ Fill robots values with values read from server """

        self.ssk_flag = values_dict[Keys.SSK_FLAG]
        self.robot_update_flag = values_dict[Keys.ROBOT_UPDATE_FLAG]
        if self.ssk_flag == SskState.KILL:
            self.robot_update_flag = RobotUpdateFlag.IDLE
        self.robot_name = values_dict[Keys.ROBOT_NAME]
        # Condition to prevent overwriting state by background threat (async communication with bot)
        if ((self.state == StateState.STOPPED and values_dict[Keys.STATE] == StateState.STOPPING)
                or (self.result != "-" and (not self.running) and self.state == StateState.ACTIVE)):
            self.state = StateState.STOPPED
            self.ssk_flag = SskState.IDLE
        else:
            self.state = values_dict[Keys.STATE]


    def choose_operation(self):
        """ Choose operation START/STOP/KILL/IDLE based on ssk_flag boolean value """

        if self.ssk_flag == SskState.START:
            self.start()
        elif self.ssk_flag == SskState.STOP:
            if self.running:
                self.stop()
        elif self.ssk_flag == SskState.KILL:
            if self.running:
                self.kill()
        elif self.ssk_flag == SskState.IDLE:
            pass
        else:
            app.logger.log(f"Received incorrect value of ssk_flag -> '{self.ssk_flag}'")

    def read_from_bot(self):
        """ Read info from bot (used in background thread) """

        if not self.running:
            return None
        while True:
            data_from_bot = self.bot.stdout.readline().strip()
            if not data_from_bot:
                continue
            if data_from_bot.startswith("RESULT:"):
                self.running = False
                if self.state == StateState.STOPPING or self.state == StateState.ACTIVE:
                    self.state = StateState.STOPPED
                    app.logger.log("Bot stopped")
                self.result = data_from_bot[7:]
                if self.result == "":
                    self.result = "Empty result from bot, check logs"
            elif data_from_bot == "BOT STARTED":
                self.running = True
            else:
                app.logger.log("Received incorrect data from bot")

    def write_to_bot(self, message: str = ""):
        """ Write info to bot (used to send STOP signal for close bot in correct time) """

        if not self.running:
            return None
        self.bot.stdin.write(f'{message}\n')
        self.bot.stdin.flush()

    def start(self):
        """ START operations with start subprocess (bot) and background thread for communication with bot"""

        self.ssk_flag = SskState.IDLE
        self.running = True
        self.state = StateState.ACTIVE
        self.result = "-"
        self.robot_update_flag = RobotUpdateFlag.IDLE

        subprocess_path = self.get_subprocess_path_from_main_file_location()
        self.bot = subprocess.Popen([
                app.config.bot_venv_path,
                subprocess_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if not self.input_thread:
            self.input_thread = threading.Thread(target=self.read_from_bot, daemon=True)
            self.input_thread.start()
        app.logger.log("Bot started")

    @staticmethod
    def get_subprocess_path_from_main_file_location():
        """ Specify path to subprocess main.py:
            - Try to find it in bot folder
            - If cannot find in bot folder try to find it in folder (if single folder in bot folder)
        """

        files_and_folders_list = os.listdir(app.config.bot_path)
        if "main.py" in files_and_folders_list:
            return f"{app.config.bot_path}\\main.py"
        if len(files_and_folders_list) != 1:
            raise Exception("Incorrect bot files arrangement")
        subfolder_path = f"{app.config.bot_path}\\{files_and_folders_list[0]}"
        if not os.path.exists(subfolder_path):
            raise Exception("Incorrect bot files arrangement")
        files_in_subfolder_list = os.listdir(subfolder_path)
        if "main.py" in files_in_subfolder_list:
            return f"{subfolder_path}\\main.py"
        else:
            raise Exception("Incorrect bot files arrangement")

    def stop(self):
        """ Send info to bot and wait to close"""

        if self.running:
            self.ssk_flag = SskState.IDLE
            self.state = StateState.STOPPING
            self.result = "-"
            self.write_to_bot("STOP")
            app.logger.log("Send stop signal to bot")

    def kill(self):
        """ Kill subprocess without waiting for its safe close """
        self.robot_update_flag = RobotUpdateFlag.IDLE
        if self.running:
            self.ssk_flag = SskState.IDLE
            self.running = False
            self.state = StateState.KILLED
            self.result = "-"
            app.logger.log("Bot killed")

    def close_processes_if_not_running(self):
        if not self.running:
            if self.bot:
                self.bot.terminate()
                self.bot.wait()

    def update_if_required(self):
        """ -Check robot update flag, if set try to stop bot (if not stopped or killed)
            - Download file from server to temp folder
            - Delete old files from bot folder
            - Unzip bot from temp folder to bot folder
            - Delete temp folder
        """
        if self.robot_update_flag != RobotUpdateFlag.UPDATE:
            return None
        if self.state != StateState.STOPPED and self.state != StateState.KILLED:
            self.ssk_flag = SskState.STOP
            return None
        try:
            app.logger.log(f"Start download bot file '{self.robot_name}'")
            temp_file_path = app.request_func.download_robot(self.robot_name)
            app.logger.log(f"Bot downloaded successfully")
            self.delete_old_bot_files()
            app.logger.log(f"Old bot files removed successfully")
            self.unzip_bot(temp_file_path)
            app.logger.log(f"New bot unzipped successfully")
            self.delete_temp_folder()
            app.logger.log(f"Robot updated successfully")
            self.robot_update_flag = RobotUpdateFlag.IDLE
            self.result = "Robot updated"
            app.download_retries = 0
        except Exception as e:
            raise UpdateException(e)



    @staticmethod
    def delete_old_bot_files():
        bot_folder_path = app.config.bot_path
        if os.path.exists(bot_folder_path):
            shutil.rmtree(bot_folder_path)
        os.makedirs(bot_folder_path)

    @staticmethod
    def unzip_bot(file_to_unzip: str):
        destination_files_path = app.config.bot_path
        if file_to_unzip.endswith(".zip"):
            with zipfile.ZipFile(file_to_unzip, 'r') as unzipping_file:
                unzipping_file.extractall(destination_files_path)
        else:
            app.logger.log("Incorrect file format (allowed only .zip or .rar)")

    @staticmethod
    def delete_temp_folder():
        temp_bot_path = app.config.temp_path
        if os.path.exists(temp_bot_path):
            shutil.rmtree(temp_bot_path)
