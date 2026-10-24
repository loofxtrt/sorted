from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from src.utils.generic import is_image

# TODO: documentação
def set_pixmap_size(pixmap: QPixmap, width: int=100, height: int | None = None) -> QPixmap:
    if not height:
        height = width

    return pixmap.scaled(
        width, height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation # anti-aliasing TODO: fazer ser desligável
    )

def image_to_label(file: Path) -> QLabel | None:
    if is_image(file):
        pixmap = QPixmap(str(file))

        label = QLabel()
        label.setPixmap(pixmap)

        return label

    return None
