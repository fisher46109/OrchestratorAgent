import os
import traceback
import datetime


def main():
    output = ""
    try:
        from agent import execute
        execute()
        output = "Success"
    except Exception as e:
        try:
            output = get_exception_info(e)
        except:
            pass
        try:
            log_fatal(output)
        except:
            """DO NOTHING, If this doesn't work - nothing will save us..."""
    finally:
        try:
            print(str(output)) # TODO other operations to handle fatal
        except:
            pass


def get_exception_info(exception: Exception):
    """ Returns string representations of exception message with it's traceback."""
    source = ""
    for tb in reversed(traceback.extract_tb(exception.__traceback__)):
        short_filename = tb.filename.split('\\')[-1]
        source = f"{source} @ {short_filename}/{tb.name}#{tb.lineno}"
    return f"[{type(exception).__name__}] {exception}{source}"


def log_fatal(message):
    """ Appends a line with fatal exception into the fatal log file on the desktop. If the file does not exist, it
    will be created."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    host = os.environ["COMPUTERNAME"]
    username = os.environ["USERNAME"]
    log_line = f"timestamp={timestamp} ; " \
               f"host={host} ; " \
               f"username={username} ; " \
               f"level=FATAL ; " \
               f"source=main ; " \
               f"message={message}"

    if os.path.exists(f"{os.path.dirname(__file__)}"):
        path_fatal_log_file = f"{os.path.dirname(__file__)}\\FatalLog.txt"

    with open(path_fatal_log_file, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')


if __name__ == '__main__':
    main()
