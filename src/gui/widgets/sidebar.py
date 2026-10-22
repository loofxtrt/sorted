from pathlib import Path

from PyQt6.QtWidgets import QWidget, QTabWidget, QHBoxLayout, QTreeView
from PyQt6.QtGui import QFileSystemModel

class Sidebar(QWidget):
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.vault_widget = QWidget()
        layout.addWidget(self.vault_widget)

        self.entry_widget = QWidget()
        layout.addWidget(self.entry_widget)

        self.file_tree = self.compose_file_tree(str(root))
        layout.addWidget(self.file_tree)

    def compose_file_tree(self, root: str) -> QTreeView:
        self.model = QFileSystemModel()
        self.model.setRootPath(root)

        tree = QTreeView()
        tree.setModel(self.model)

        tree.setRootIndex(self.model.index(root))

        tree.setHeaderHidden(True)
        tree.hideColumn(1)
        tree.hideColumn(2)
        tree.hideColumn(3)

        return tree
