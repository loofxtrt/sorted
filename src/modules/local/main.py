from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from src.utils.qt import image_to_pixmap, label_with_pixmap, set_pixmap_size

from ...managers.models import Module, Vault, Entry
from ...utils.generic import is_image

class LocalModule(Module):
    # TODO: documentação
    def __init__(self, vault: Vault):
        super().__init__(
            id='local',
            vault=vault,
            supported_types=['file']
        )

    def build_entry_widget(self, entry: Entry) -> QWidget:
        path = Path(entry.reference)

        # layout
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        # adicionar uma thumbnail caso seja uma imagem
        if path.is_file() and is_image(path):
            # TODO: fallback
            pixmap = image_to_pixmap(path, validate_image=False)
            pixmap = set_pixmap_size(pixmap)

            thumbnail = label_with_pixmap(pixmap)

            layout.addWidget(thumbnail)

        # label com o nome do arquivo
        label = QLabel()
        label.setText(path.name)
        layout.addWidget(label)

        return widget
