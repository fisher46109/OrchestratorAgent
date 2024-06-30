import app
from request_functions import RobotUpdateFlag


class UpdateException(Exception):
    pass


def update_exception_handler(ue):
    app.download_retries += 1
    if app.download_retries > app.config.max_download_bot_retries:
        app.download_retries = 0
        app.logger.log("Max retries number of updating bot exceeded!")
        app.bot.robot_update_flag = RobotUpdateFlag.IDLE
        app.bot.result = "Robot updating failed! Check logs."
        app.request_func.update_all()

    else:
        app.logger.log(f"Cannot update file -> {ue}")
        app.logger.log(f"Start {app.download_retries} of {app.config.max_download_bot_retries} retries...")
