import subprocess
import threading
from request_functions import StateState, SskState
import app


class BotHandler:
    """ Class to handle all operations with bot (subprocess) """

    def __init__(self):
        self.ssk_flag = SskState.IDLE
        self.running = False
        self.state = StateState.IDLE
        self.result = "-"
        self.robot_update_flag = "-"
        # None initialization of subprocess (bot)
        self.bot: subprocess.Popen | None = None
        # None initialization of background thread to read info from subprocess (bot)
        self.input_thread: threading.Thread | None = None

    def __str__(self):
        return (f"Running: {self.running}\t"
                f"State: {self.state}\t"
                f"Result: {self.result}\t")

    def choose_operation(self, ssk_flag: str = ""):
        """ Choose operation START/STOP/KILL/IDLE based on ssk_flag boolean value """

        if ssk_flag == SskState.START:
            self.start()
        elif ssk_flag == SskState.STOP:
            if self.running:
                self.stop()
        elif ssk_flag == SskState.KILL:
            if self.running:
                self.kill()
        elif ssk_flag == SskState.IDLE:
            pass
        else:
            app.logger.log(f"Received incorrect value of ssk_flag -> '{ssk_flag}'")

    def read_from_bot(self):
        """ Read info from bot (used in background thread) """

        if not self.running:
            return None
        while True:
            data_from_bot = self.bot.stdout.readline().strip()
            if data_from_bot.startswith("RESULT:"):
                self.running = False
                if self.state == StateState.STOPPING:
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
        self.bot = subprocess.Popen([
                app.config.bot_venv_path,
                app.config.bot_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.input_thread = threading.Thread(target=self.read_from_bot, daemon=True)
        self.input_thread.start()
        app.logger.log("Bot started")

    def stop(self):
        """ send info to bot and wait to close"""
        if self.running:
            self.ssk_flag = SskState.IDLE
            self.state = StateState.STOPPING
            self.result = "-"
            self.write_to_bot("STOP")
            app.logger.log("Send stop signal to bot")

    def kill(self):
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

