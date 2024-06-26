import time
from request_functions import RequestFunctions, Keys
from app import BotHandler, Config, Logger
import app


def execute():
    app.config = Config()
    app.config.load_config()

    app.logger = Logger()
    app.logger.log("Start of working agent")

    # Initialization class to handle communication with orchestrator
    request_func = RequestFunctions(app.config.orchestrator_url, app.config.user_name, app.config.machine_name)

    # Initialization class to handle communication with bot
    app.bot = BotHandler()


    while True:
        try:
            data_from_orchestrator = request_func.get_info()
            ssk_flag = data_from_orchestrator[Keys.SSK_FLAG]

            # Choose START/STOP/KILL/IDLE
            app.bot.choose_operation(ssk_flag)

            request_func.update_all(ssk_flag=app.bot.ssk_flag,
                                    state=app.bot.state,
                                    result=app.bot.result,
                                    robot_update_flag=app.bot.robot_update_flag)

            app.bot.close_processes_if_not_running()

            time.sleep(app.config.time_between_requests)
        except Exception as e:
            app.logger.log(e)
