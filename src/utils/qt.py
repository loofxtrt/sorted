from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from src.utils.generic import is_image

# TODO: documentação
def set_pixmap_size(pixmap: QPixmap, width: int=100, height: int | None = None) -> QPixmap:
    """
    redimensiona um pixmap mantendo a proporção original
    o resultado cabe dentro de width x height, então pode ficar menor que isso em uma das dimensões

    args:
        pixmap:
            pixmap que será redimensionado

        width:
            largura máxima do resultado

        height:
            altura máxima do resultado
            se for None (ou 0), usa o mesmo valor de width

    returns:
        um novo pixmap redimensionado, com suavização (anti-aliasing)
    """

    if not height:
        height = width

    return pixmap.scaled(
        width, height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation # anti-aliasing TODO: fazer ser desligável
    )

def image_to_pixmap(file: Path, validate_image: bool = True) -> QPixmap | None:
    """
    carrega um arquivo de imagem como pixmap

    args:
        file:
            caminho do arquivo de imagem

        validate_image:
            se for True, verifica se o arquivo é uma imagem antes de carregar

    returns:
        o pixmap carregado, ou None se a validação estiver ativa e o arquivo não for uma imagem
    """

    if validate_image:
        if not is_image(file):
            return None

    return QPixmap(str(file))

def label_with_pixmap(pixmap: QPixmap) -> QLabel | None:
    """
    cria um label que exibe um pixmap

    args:
        pixmap:
            pixmap que será exibido no label

    returns:
        o label criado
    """

    label = QLabel()
    label.setPixmap(pixmap)

    return label
