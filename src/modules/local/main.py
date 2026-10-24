from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from src.utils.qt import image_to_pixmap, label_with_pixmap, set_pixmap_size

from ...managers.models import Module, Vault, Entry
from ...utils.generic import is_image

class LocalModule(Module):
    # TODO: documentação
    # TODO: suporte a referências relativas
    # TODO: details ser desligável
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

        if path.is_file():
            name_text = path.name
            details_text = str(path.stat().st_size)

            if is_image(path):
                # adicionar uma thumbnail caso seja uma imagem
                # TODO: fallback
                pixmap = image_to_pixmap(path, validate_image=False)
                pixmap = set_pixmap_size(pixmap)

                thumbnail = label_with_pixmap(pixmap)

                layout.addWidget(thumbnail)
        else:
            name_text = 'Reference error'
            details_text = f'\'{path}\' is not a valid system file path'

        # label com o nome do arquivo
        name_label = QLabel(name_text)
        layout.addWidget(name_label)

        # label com detalhes
        details_label = QLabel(details_text)
        layout.addWidget(details_label)

        return widget
