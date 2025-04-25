import colorlog
import sys

class Logger:
    def __init__(self, name, show_date=True):
    
        if show_date:
            self.datefmt='%Y-%m-%d %H:%M:%S'
            self.log_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            self.datefmt=''
            self.log_format = '%(message)s'

        self.logger = colorlog.getLogger(name)

        self.log_colors = {
            'DEBUG': 'light_black',
            'INFO': 'black',
            'WARNING': 'bold_purple',
            'ERROR': 'red',
            'CRITICAL': 'bold_red,bg_white',
            'MESSAGE' : 'green'
        }

        # Configuration for the logs manager with color
        handler = colorlog.StreamHandler(sys.stdout)

        # Formatter with colorconfiguration and adding a timestamp
        color_formatter = colorlog.ColoredFormatter(
            self.log_format,
            datefmt=self.datefmt,
            log_colors=self.log_colors
        )

        handler.setFormatter(color_formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(colorlog.DEBUG)

    def debug(self, message, flush=True):
        self.logger.debug(message)
        if flush:
            self.flush()

    def info(self, message, flush=True):
        self.logger.info(message)
        if flush:
            self.flush()

    def warning(self, message, flush=True):
        self.logger.warning(message)
        if flush:
            self.flush()

    def error(self, message, flush=True):
        self.logger.error(message)
        if flush:
            self.flush()

    def critical(self, message, flush=True):
        self.logger.critical(message)
        if flush:
            self.flush()

    def message(self, message, flush=True):
        self.logger.log(20, message, extra={'log_color': 'MESSAGE'})
        if flush:
            self.flush()

    def flush(self):
        """We want the logger print message inmediately"""
        for handler in self.logger.handlers:
            handler.flush()