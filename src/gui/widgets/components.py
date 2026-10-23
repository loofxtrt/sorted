from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

def build_error_entry_widget(main_text: str = 'Entry not found', details_text: str | None = None) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)

    main_font = QFont()
    main_font.setPointSize(14)
    # main_font.setBold(True)

    main_label = QLabel(main_text)
    main_label.setFont(main_font)
    layout.addWidget(main_label)

    if details_text:
        layout.addWidget(QLabel(details_text))

    layout.addStretch()

    return widget
