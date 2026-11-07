from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
)
from models import Order


class BaseDialog(QDialog):
    def __init__(self, title, min_width, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(min_width)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(12)

    def add_heading(self, text):
        heading = QLabel(text)
        heading.setObjectName("dialogTitle")
        self.main_layout.addWidget(heading)
        return heading

    def field_label(self, text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def add_buttons(self, ok_text, with_cancel=True):
        row = QHBoxLayout()
        if with_cancel:
            btn_cancel = QPushButton("Cancel")
            btn_cancel.setObjectName("secondary")
            btn_cancel.clicked.connect(self.reject)
            row.addWidget(btn_cancel)
        btn_ok = QPushButton(ok_text)
        btn_ok.clicked.connect(self.accept)
        row.addWidget(btn_ok)
        self.main_layout.addLayout(row)


class ConfirmOrderDialog(BaseDialog):
    def __init__(self, customer_name, phone, source, job_details, total_cost, parent=None):
        super().__init__("Confirm Order Submission", 380, parent)
        self.add_heading("Confirm Your Order")

        card = QFrame()
        card.setObjectName("dialogCard")
        form = QFormLayout(card)
        form.setSpacing(8)
        form.addRow(self.field_label("Customer Name:"), QLabel(customer_name))
        form.addRow(self.field_label("Contact Number:"), QLabel(phone or "N/A"))
        form.addRow(self.field_label("File Source:"), QLabel(source))

        job = QLabel(job_details)
        job.setWordWrap(True)
        form.addRow(self.field_label("Order Details:"), job)

        cost = QLabel(total_cost)
        cost.setObjectName("dialogTotal")
        form.addRow(self.field_label("Total Cost:"), cost)

        self.main_layout.addWidget(card)
        self.add_buttons("Confirm & Submit")


class CustomAlertDialog(BaseDialog):
    def __init__(self, title_text, message_text, parent=None):
        super().__init__(title_text, 300, parent)
        self.add_heading(title_text)

        message = QLabel(message_text)
        message.setWordWrap(True)
        self.main_layout.addWidget(message)
        self.add_buttons("OK", with_cancel=False)


class UpdateStatusDialog(BaseDialog):
    def __init__(self, order_id, current_status="Pending", parent=None):
        super().__init__(f"Update Order {order_id}", 320, parent)
        self.add_heading(f"Order #{order_id}")

        self.combo_status = QComboBox()
        self.combo_status.addItems(Order.STATUSES)
        self.combo_status.setCurrentText(current_status)

        form = QFormLayout()
        form.addRow(self.field_label("Set Status:"), self.combo_status)
        self.main_layout.addLayout(form)
        self.add_buttons("Save")

    def get_selected_status(self):
        return self.combo_status.currentText()