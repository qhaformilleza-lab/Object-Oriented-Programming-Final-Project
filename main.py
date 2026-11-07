import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from admin_screen import AdminWindow
from models import OrderLog, PriceList
from user_screen import UserWindow


def resource_dir():
    if getattr(sys, "_MEIPASS", None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def load_style(app, base_dir):
    qss_path = os.path.join(base_dir, "style.qss")
    if not os.path.exists(qss_path):
        print(f"Warning: Could not find QSS file at {qss_path}")
        return
    background_url = os.path.join(base_dir, "darkwindows.png").replace("\\", "/")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read().replace("url(darkwindows.png)", f'url("{background_url}")'))


def main():
    app = QApplication(sys.argv)
    base_dir = resource_dir()
    load_style(app, base_dir)

    icon_path = os.path.join(base_dir, "Print icon.png")
    icon = QIcon(icon_path) if os.path.exists(icon_path) else None
    if icon is not None:
        app.setWindowIcon(icon)

    prices = PriceList.load()
    order_log = OrderLog()
    user_win = UserWindow(prices, order_log)
    admin_win = AdminWindow(prices, order_log)
    if icon is not None:
        user_win.setWindowIcon(icon)
        admin_win.setWindowIcon(icon)
    user_win.peer = admin_win
    admin_win.peer = user_win

    screens = app.screens()
    if len(screens) >= 2:
        user_win.setScreen(screens[0])
        user_win.showMaximized()
        admin_win.setScreen(screens[1])
        admin_win.showMaximized()
    else:
        user_win.show()
        admin_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()