from flaskmyapp import app, my_web_app, authenication, __init__
from logging import getLogger, Formatter, FileHandler, DEBUG, StreamHandler

formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler = StreamHandler()
file_handler.setFormatter(formatter)


app_logger = getLogger(__name__)
app_logger.addHandler(file_handler)
app_logger.setLevel(DEBUG)

app_logger.debug("debug message from app.py")
app_logger.info("info message from app.py")
app_logger.warning("warn message from app.py")

my_web_app_logger = getLogger("my_web_app")
my_web_app_logger.addHandler(file_handler)
my_web_app_logger.setLevel(DEBUG)

authenication_logger = getLogger(authenication)
authenication_logger.addHandler(file_handler)
authenication_logger.setLevel(DEBUG)

__init__logger = getLogger(__init__)
__init__logger.addHandler(file_handler)
__init__logger.setLevel(DEBUG)
my_web_app.log()
authenication.log()
__init__.log()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)