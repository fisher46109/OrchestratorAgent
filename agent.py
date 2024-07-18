import time
import app
from config import Config
from custom_exceptions import UpdateException, update_exception_handler
from logger import Logger
from request_functions import RequestFunctions
from subproces_handler import BotHandler
from requests.exceptions import ConnectionError, HTTPError


def execute():
    app.config = Config()
    app.config.load_config()
    # print(app.config)

    app.logger = Logger()
    app.logger.log("Start of working agent")

    # Initialization class to handle communication with orchestrator
    app.request_func = RequestFunctions(app.config.orchestrator_url, app.config.user_name, app.config.machine_name)

    # Initialization class to handle communication with bot
    app.bot = BotHandler()

    while True:
        try:
            app.bot.set_control_values(app.request_func.get_info())
            # print(app.bot)
            app.bot.update_if_required()
            app.bot.choose_operation()
            app.request_func.update_all()
            app.bot.close_processes_if_not_running()
            time.sleep(app.config.time_between_requests)
        except (ConnectionError, HTTPError) as ce:
            app.logger.log(str(ce))
            time.sleep(app.config.time_if_connection_error)
        except UpdateException as ue:
            update_exception_handler(ue)
        except Exception as e:
            # print(type(e))
            app.logger.log(str(e))
