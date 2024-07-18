from subproces_handler import BotHandler
from config import Config
from logger import Logger
from request_functions import RequestFunctions

bot: BotHandler | None = None
config: Config | None = None
logger: Logger | None = None
request_func: RequestFunctions | None = None

download_retries = 0
