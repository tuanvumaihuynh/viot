import logging


def init_logger() -> None:
    fmt = (
        "\x1b[32m%(asctime)s\x1b[0m | "
        "%(levelname)-8s\x1b[0m | "
        "\x1b[36m%(name)s\x1b[0m:\x1b[36m%(funcName)s\x1b[0m:\x1b[36m%(lineno)d\x1b[0m - %(message)s\x1b[0m"
    )

    level = logging.DEBUG

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(ColorizedFormatter(fmt))
    logging.basicConfig(level=level, handlers=[console_handler])


class ColorizedFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    bold = "\x1b[1m"
    grey = f"{bold}\x1b[38;21m"
    blue = f"{bold}\x1b[38;5;39m"
    yellow = f"{bold}\x1b[38;5;229m"
    red = f"{bold}\x1b[38;5;203m"
    bold_red = f"{bold}\x1b[31;1m"

    def __init__(self, fmt: str):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.blue,
            logging.INFO: self.grey,
            logging.WARNING: self.yellow,
            logging.ERROR: self.red,
            logging.CRITICAL: self.bold_red,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(self.fmt)
        record.levelname = log_fmt + record.levelname
        record.msg = log_fmt + record.msg
        return formatter.format(record)
