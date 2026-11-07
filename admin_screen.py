from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from base_window import BaseWindow
from dialogs import CustomAlertDialog, UpdateStatusDialog
from models import Order


class AdminWindow(BaseWindow):
    COLUMNS = ["# Order", "Customer Info", "Job Details", "Source", "Amount", "Status", "Action"]
    ACTION_COLUMN = 6
    ALL_STATUSES = "All Statuses"

    def __init__(self, prices, order_log):
        super().__init__("PrintSync - Admin Dashboard", prices, order_log)
        self.orders = []
        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        self.tabs = QTabWidget()
        self.tabs.tabBar().setDrawBase(False)
        self.tabs.addTab(self.build_main_page(), "Main Queue")
        self.tabs.addTab(self.build_price_page(), "Change Prices")
        self.setCentralWidget(self.tabs)

    def make_card(self, title):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        caption = QLabel(title)
        caption.setObjectName("cardTitle")
        value = QLabel("0")
        value.setObjectName("cardValue")
        layout.addWidget(caption)
        layout.addWidget(value)
        return card, value

    def build_main_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        card_sales, self.label_sales = self.make_card("Sales Today")
        card_orders, self.label_orders = self.make_card("Total Orders")
        card_jobs, self.label_jobs = self.make_card("Open Jobs")
        for card in (card_sales, card_orders, card_jobs):
            cards.addWidget(card)

        title = QLabel("Orders Queue")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Live job queue and transaction history in one place. Use the filter to focus on a stage.")
        subtitle.setObjectName("subtitle")

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search name or order code...")
        self.combo_filter = QComboBox()
        self.combo_filter.addItems([self.ALL_STATUSES] + Order.STATUSES)
        filters = QHBoxLayout()
        filters.setSpacing(10)
        filters.addWidget(self.txt_search, 1)
        filters.addWidget(self.combo_filter)

        self.table = QTableWidget()
        self.table.setObjectName("ordersTable")
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.txt_search.textChanged.connect(self.refresh_table)
        self.combo_filter.currentIndexChanged.connect(self.refresh_table)
        self.table.cellClicked.connect(self.cell_clicked)

        layout.addLayout(cards)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(filters)
        layout.addWidget(self.table)
        return page

    def build_price_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Change Prices")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Press Save to use the new prices on the user screen.")
        subtitle.setObjectName("subtitle")

        form = QFormLayout()
        self.price_spins = []
        for _key, label, _default in self.prices.ITEMS:
            spin = QSpinBox()
            spin.setRange(0, 999)
            spin.setPrefix("₱")
            caption = QLabel(label)
            caption.setObjectName("formLabel")
            form.addRow(caption, spin)
            self.price_spins.append(spin)
        self.on_prices_changed()

        btn_save = QPushButton("Save Prices")
        btn_save.clicked.connect(self.save_prices)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(btn_save)
        layout.addStretch()
        return page

    def refresh_table(self):
        status = self.combo_filter.currentText()
        search = self.txt_search.text()
        shown = [
            order for order in self.orders
            if order.matches(search) and (status == self.ALL_STATUSES or order.status == status)
        ]

        self.table.setRowCount(len(shown))
        for row, order in enumerate(shown):
            customer = "\n".join(part for part in (order.name, order.phone, order.account) if part)
            cells = [order.id, customer, order.job, order.source, f"₱{order.amount:.0f}", order.status, "Update"]
            for column, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if column == self.ACTION_COLUMN:
                    item.setForeground(QColor("#0969da"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.table.setItem(row, column, item)
        self.table.resizeRowsToContents()

        self.label_sales.setText(f"₱{sum(order.amount for order in self.orders if order.counts_as_sale):.0f}")
        self.label_orders.setText(str(len(self.orders)))
        self.label_jobs.setText(str(sum(1 for order in self.orders if order.is_open)))

    def cell_clicked(self, row, column):
        if column != self.ACTION_COLUMN:
            return
        order = self.find_order(self.table.item(row, 0).text())
        if order:
            self.update_status(order)

    def find_order(self, order_id):
        return next((order for order in self.orders if order.id == order_id), None)

    def update_status(self, order):
        dialog = UpdateStatusDialog(order.id, order.status, self)
        if not dialog.exec():
            return
        new_status = dialog.get_selected_status()
        if new_status == order.status:
            return
        order.status = new_status
        self.save_history(self.order_log.record_status(order))
        self.refresh_table()
        if self.peer:
            self.peer.on_status_changed(order)

    def save_history(self, saved):
        if not saved:
            CustomAlertDialog("History Not Saved", "The change was made, but orders.txt could not be written.", self).exec()

    def on_order_placed(self, order):
        self.orders.append(order)
        self.save_history(self.order_log.record_order(order))
        self.refresh_table()

    def on_prices_changed(self):
        for spin, value in zip(self.price_spins, self.prices.values()):
            spin.setValue(value)

    def save_prices(self):
        self.prices.set_values([spin.value() for spin in self.price_spins])
        saved = self.prices.save()
        if self.peer:
            self.peer.on_prices_changed()
        if saved:
            CustomAlertDialog("Prices Saved", "The user screen now uses the new prices.", self).exec()
        else:
            CustomAlertDialog(
                "Prices Not Saved",
                "The user screen uses the new prices, but price.txt could not be written, so they will reset when the app closes.",
                self,
            ).exec()