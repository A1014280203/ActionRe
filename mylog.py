import logging
from PyQt5.QtWidgets import QPlainTextEdit


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()

        self.widget = QPlainTextEdit(parent)
        self.widget.setGeometry(300, 300, 600, 400)
        self.widget.setReadOnly(True)
        self.widget.setWindowTitle('Log View')
        self.widget.show()

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self):
        pass


class ConsolePanelHandler(logging.Handler):

    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.parent = parent

    def emit(self, record):
        self.parent.write(self.format(record))
