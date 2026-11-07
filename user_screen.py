from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from base_window import BaseWindow
from dialogs import ConfirmOrderDialog, CustomAlertDialog
from models import Order


class UserWindow(BaseWindow):
    SIZES = [("Letter / Short", "paper"), ("A4", "paper"), ("Legal / Long", "legal"), ("Photo Paper", "photo")]
    COLORS = [("Black and White", "bw", "B&W"), ("Full Color", "color", "Full Color")]
    ADDONS = [("Binding", "binding"), ("Lamination", "lamination")]
    SOURCES = ["Gmail", "Facebook / Messenger"]

    def __init__(self, prices, order_log):
        super().__init__("PrintSync - User Kiosk", prices, order_log)
        self.order_count = order_log.last_number()
        self.build_ui()
        self.on_prices_changed()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("New Print Order Form")
        title.setObjectName("title")
        subtitle = QLabel("Select options below to compute total price.")
        subtitle.setObjectName("subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        columns = QHBoxLayout()
        columns.setSpacing(16)
        columns.addLayout(self.build_form(), 1)
        columns.addLayout(self.build_right_panel(), 1)
        root.addLayout(columns)

    def labeled(self, text, widget):
        column = QVBoxLayout()
        column.setSpacing(6)
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        column.addWidget(label)
        column.addWidget(widget)
        return column

    def build_form(self):
        form = QVBoxLayout()
        form.setSpacing(12)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Juan Dela Cruz")
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("0917-XXX-XXXX")
        self.txt_account = QLineEdit()
        self.txt_account.setPlaceholderText("Email or FB Username")

        customer_row = QHBoxLayout()
        customer_row.setSpacing(12)
        customer_row.addLayout(self.labeled("Customer Name *", self.txt_name), 1)
        customer_row.addLayout(self.labeled("Contact Number", self.txt_phone), 1)
        form.addLayout(customer_row)
        form.addLayout(self.labeled("Email / FB Account", self.txt_account))

        source_label = QLabel("File Submission Source:")
        source_label.setObjectName("fieldLabel")
        source_row = QHBoxLayout()
        source_row.setSpacing(8)
        self.source_group = QButtonGroup(self)
        self.source_group.setExclusive(True)
        for text in self.SOURCES:
            button = QPushButton(text)
            button.setObjectName("sourceButton")
            button.setCheckable(True)
            button.setFixedHeight(36)
            self.source_group.addButton(button)
            source_row.addWidget(button, 1)
        self.source_group.buttons()[0].setChecked(True)
        form.addWidget(source_label)
        form.addLayout(source_row)

        spec_title = QLabel("Print Specifications")
        spec_title.setObjectName("sectionTitle")
        form.addWidget(spec_title)

        self.combo_color = QComboBox()
        self.combo_color.addItems([name for name, _key, _short in self.COLORS])
        self.combo_size = QComboBox()
        self.combo_size.addItems([name for name, _key in self.SIZES])

        spec_row1 = QHBoxLayout()
        spec_row1.setSpacing(12)
        spec_row1.addLayout(self.labeled("Color Mode", self.combo_color), 1)
        spec_row1.addLayout(self.labeled("Paper Size", self.combo_size), 1)
        form.addLayout(spec_row1)

        self.spin_pages = QSpinBox()
        self.spin_pages.setRange(1, 1000)
        self.spin_pages.setValue(10)
        self.spin_copies = QSpinBox()
        self.spin_copies.setRange(1, 100)
        self.spin_copies.setValue(1)

        spec_row2 = QHBoxLayout()
        spec_row2.setSpacing(12)
        spec_row2.addLayout(self.labeled("Pages", self.spin_pages), 1)
        spec_row2.addLayout(self.labeled("Copies", self.spin_copies), 1)
        form.addLayout(spec_row2)

        self.addon_boxes = []
        addons_row = QHBoxLayout()
        addons_row.setSpacing(16)
        for _name, _key in self.ADDONS:
            box = QCheckBox()
            addons_row.addWidget(box)
            self.addon_boxes.append(box)
        form.addLayout(addons_row)

        self.combo_color.currentIndexChanged.connect(self.calculate_total)
        self.combo_size.currentIndexChanged.connect(self.calculate_total)
        self.spin_pages.valueChanged.connect(self.calculate_total)
        self.spin_copies.valueChanged.connect(self.calculate_total)
        for box in self.addon_boxes:
            box.toggled.connect(self.calculate_total)

        form.addStretch()
        return form

    def build_right_panel(self):
        panel = QVBoxLayout()
        panel.setSpacing(12)

        price_title = QLabel("Price Breakdown")
        price_title.setObjectName("sectionTitle")
        panel.addWidget(price_title)

        self.lbl_breakdown = QLabel()
        self.lbl_breakdown.setObjectName("breakdown")
        panel.addWidget(self.lbl_breakdown)

        self.lbl_total = QLabel("₱0")
        self.lbl_total.setObjectName("total")
        panel.addWidget(self.lbl_total)

        self.btn_place_order = QPushButton("Place Order")
        self.btn_place_order.setObjectName("placeOrder")
        self.btn_place_order.clicked.connect(self.place_order)
        panel.addWidget(self.btn_place_order)

        status_title = QLabel("Order Status")
        status_title.setObjectName("sectionTitle")
        panel.addWidget(status_title)

        self.status_table = QTableWidget()
        self.status_table.setObjectName("statusTable")
        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(["Order", "Job", "Status"])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.status_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        panel.addWidget(self.status_table)
        return panel

    def on_prices_changed(self):
        for index, (name, key) in enumerate(self.SIZES):
            self.combo_size.setItemText(index, f"{name} — ₱{self.prices.get(key):.2f}/pg")
        for index, (name, key, _short) in enumerate(self.COLORS):
            self.combo_color.setItemText(index, f"{name} — +₱{self.prices.get(key):.2f}/pg")
        for box, (name, key) in zip(self.addon_boxes, self.ADDONS):
            box.setText(f"{name} (+₱{self.prices.get(key)})")
        self.calculate_total()

    def calculate_total(self):
        size_name, size_key = self.SIZES[self.combo_size.currentIndex()]
        _color_name, color_key, color_short = self.COLORS[self.combo_color.currentIndex()]
        pages = self.spin_pages.value()
        copies = self.spin_copies.value()

        paper_cost = self.prices.get(size_key)
        print_cost = self.prices.get(color_key)
        paper_total = pages * paper_cost
        color_total = pages * print_cost

        chosen = self.chosen_addons()
        addon_cost = sum(self.prices.get(key) for _name, key in chosen)
        addons_text = ", ".join(name for name, _key in chosen) or "None"

        per_copy = paper_total + color_total + addon_cost
        total = per_copy * copies
        copy_word = "copy" if copies == 1 else "copies"

        self.lbl_breakdown.setText(
            f"• Base Paper ({size_name}): {pages} pgs × ₱{paper_cost:.2f} = ₱{paper_total:.2f}\n"
            f"• Color Option ({color_short}): {pages} pgs × ₱{print_cost:.2f} = ₱{color_total:.2f}\n"
            f"• Add-ons: {addons_text} = ₱{addon_cost:.2f}\n"
            f"• Multiplier: ₱{per_copy:.2f} × {copies} {copy_word}"
        )
        self.lbl_total.setText(f"₱{total:.0f}")
        return total

    def chosen_addons(self):
        return [addon for addon, box in zip(self.ADDONS, self.addon_boxes) if box.isChecked()]

    def job_text(self):
        size_name = self.SIZES[self.combo_size.currentIndex()][0]
        color_short = self.COLORS[self.combo_color.currentIndex()][2]
        copies = self.spin_copies.value()
        copy_word = "copy" if copies == 1 else "copies"
        parts = [f"{self.spin_pages.value()} pgs", color_short, size_name, f"{copies} {copy_word}"]
        return ", ".join(parts + [name for name, _key in self.chosen_addons()])

    def place_order(self):
        name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()
        account = self.txt_account.text().strip()
        source = self.source_group.checkedButton().text()

        if not name:
            CustomAlertDialog("Missing Info", "Please enter the customer name.", self).exec()
            self.txt_name.setFocus()
            return

        job = self.job_text()
        total = self.calculate_total()
        if not ConfirmOrderDialog(name, phone, source, job, f"₱{total:.2f}", self).exec():
            return

        self.order_count += 1
        order = Order(f"PS-{self.order_count}", name, phone, account, source, job, total)
        if self.peer:
            self.peer.on_order_placed(order)
        self.add_status_row(order)

        CustomAlertDialog("Order Placed", f"Your order {order.id} was submitted.", self).exec()
        for box in (self.txt_name, self.txt_phone, self.txt_account):
            box.clear()
        self.txt_name.setFocus()

    def add_status_row(self, order):
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        for column, text in enumerate((order.id, order.job, order.status)):
            self.status_table.setItem(row, column, QTableWidgetItem(text))

    def on_status_changed(self, order):
        for row in range(self.status_table.rowCount()):
            if self.status_table.item(row, 0).text() == order.id:
                self.status_table.item(row, 2).setText(order.status)