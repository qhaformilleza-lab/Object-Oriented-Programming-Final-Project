from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow
from dialogs import CustomAlertDialog


class BaseWindow(QMainWindow):
    def __init__(self, title, prices, order_log):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1100, 700)
        self.setMinimumSize(1100, 700)
        
        self.prices = prices
        self.order_log = order_log
        self.peer = None
        self.build_menu()

    def build_menu(self):
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.make_action("Exit", self.close))
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self.make_action("About PrintSync", self.show_about))

    def make_action(self, text, slot):
        action = QAction(text, self)
        action.triggered.connect(slot)
        return action

    def show_about(self):
        CustomAlertDialog(
            "About PrintSync",
            "PrintSync - Printing Shop Order and Transaction Management System\nBuilt with PyQt6 & OOP Principles.",
            self
        ).exec()

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()

    def on_prices_changed(self):
        pass

    def on_order_placed(self, order):
        pass

    def on_status_changed(self, order):
        pass