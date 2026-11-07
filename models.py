import os
import re
import sys
from datetime import datetime


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def data_path(name):
    return os.path.join(app_dir(), name)


class PriceList:
    ITEMS = [
        ("paper", "Letter / Short and A4 paper per page", 2),
        ("legal", "Legal / Long paper per page", 3),
        ("photo", "Photo Paper per page", 25),
        ("bw", "Black and White print per page", 2),
        ("color", "Full Color print per page", 3),
        ("binding", "Binding", 30),
        ("lamination", "Lamination", 15),
    ]
    FILE_NAME = "price.txt"

    def __init__(self):
        self._prices = {key: default for key, _label, default in self.ITEMS}

    def get(self, key):
        return self._prices.get(key, 0)

    def values(self):
        return [self._prices[key] for key, _label, _default in self.ITEMS]

    def set_values(self, values):
        if len(values) != len(self.ITEMS):
            raise ValueError("Wrong number of prices supplied.")
        numbers = [int(value) for value in values]
        if any(number < 0 for number in numbers):
            raise ValueError("Prices cannot be negative.")
        for (key, _label, _default), number in zip(self.ITEMS, numbers):
            self._prices[key] = number

    @classmethod
    def load(cls):
        prices = cls()
        folders = [app_dir()]
        if getattr(sys, "_MEIPASS", None):
            folders.append(sys._MEIPASS)
        for folder in folders:
            try:
                with open(os.path.join(folder, cls.FILE_NAME), "r", encoding="utf-8") as f:
                    prices.set_values(f.read().split())
                return prices
            except (OSError, ValueError):
                continue
        return prices

    def save(self):
        try:
            with open(data_path(self.FILE_NAME), "w", encoding="utf-8") as f:
                f.write("\n".join(str(value) for value in self.values()) + "\n")
            return True
        except OSError:
            return False


class Order:
    STATUSES = ["Pending", "Printing", "Ready for Pickup", "Completed", "Cancelled"]

    def __init__(self, order_id, name, phone, account, source, job, amount, status="Pending"):
        self.id = order_id
        self.name = name
        self.phone = phone
        self.account = account
        self.source = source
        self.job = job
        self.amount = float(amount)
        self._status = "Pending"
        self.status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in self.STATUSES:
            raise ValueError(f"Unknown status: {value}")
        self._status = value

    @property
    def is_open(self):
        return self._status not in ("Completed", "Cancelled")

    @property
    def counts_as_sale(self):
        return self._status != "Cancelled"

    def matches(self, text):
        text = text.strip().lower()
        return text in self.name.lower() or text in self.id.lower()


class OrderLog:
    FILE_NAME = "orders.txt"
    LINE = "-" * 60

    def _append(self, text):
        try:
            with open(data_path(self.FILE_NAME), "a", encoding="utf-8") as f:
                f.write(text)
            return True
        except OSError:
            return False

    @staticmethod
    def _now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def record_order(self, order):
        return self._append(
            f"[{self._now()}] NEW ORDER {order.id}\n"
            f"  Customer : {order.name}\n"
            f"  Phone    : {order.phone or 'N/A'}\n"
            f"  Account  : {order.account or 'N/A'}\n"
            f"  Source   : {order.source}\n"
            f"  Job      : {order.job}\n"
            f"  Amount   : ₱{order.amount:.2f}\n"
            f"  Status   : {order.status}\n"
            f"{self.LINE}\n"
        )

    def record_status(self, order):
        return self._append(f"[{self._now()}] STATUS {order.id} -> {order.status}\n{self.LINE}\n")

    def last_number(self, default=1000):
        try:
            with open(data_path(self.FILE_NAME), "r", encoding="utf-8") as f:
                numbers = re.findall(r"NEW ORDER PS-(\d+)", f.read())
        except OSError:
            return default
        return max([int(number) for number in numbers] + [default])