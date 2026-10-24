from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap

from src.managers.models import Entry, Module, Vault


class WebModule(Module):
    # TODO: documentação
    def __init__(self, vault: Vault):
        super().__init__(
            id='web',
            vault=vault,
            supported_types=['page']
        )

    def build_entry_widget(self, entry: Entry) -> QWidget:
        favicon_pixmap = QPixmap()

        favicon_label = QLabel()
        favicon_label.setPixmap(favicon_pixmap)

        url_label = QLabel(entry.reference) # TODO: fazer ser editável aqui também?

        widget = QWidget()
        layout = QHBoxLayout(widget)

        layout.addWidget(favicon_label)
        layout.addWidget(url_label)

        return widget
