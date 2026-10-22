from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QAbstractItemView
from pathlib import Path

from src.gui.widgets.header import Header
from src.gui.widgets.sidebar import Sidebar

class Central(QWidget):
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)

        # horizontal. ex: sidebar -> conteúdo
        layout = QHBoxLayout(self)

        self.sidebar = Sidebar(root=root)
        layout.addWidget(self.sidebar)

        # vertical. ex: header -> central logo embaixo
        self.contents = QWidget()
        self.contents_layout = QVBoxLayout(self.contents)

        self.compose_header()
        self.compose_contents()

        layout.addWidget(self.contents, 1)

    def compose_header(self):
        self.header = Header()
        self.contents_layout.addWidget(self.header)

    def compose_contents(self):
        self.qlist = QListWidget()
        self.qlist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # poder selecionar múltiplos itens

        self.contents_layout.addWidget(self.qlist, 1)
