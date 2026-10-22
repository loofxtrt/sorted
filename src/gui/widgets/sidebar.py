from pathlib import Path

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QTreeView
from PyQt6.QtGui import QFileSystemModel

from src.managers.models import Entry

class Sidebar(QWidget):
    # TODO: documentação
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.vault_widget = QWidget()
        layout.addWidget(self.vault_widget)

        self.entry_widget = QWidget()
        layout.addWidget(self.entry_widget)

        self.file_tree = self.compose_file_tree(str(root))
        layout.addWidget(self.file_tree)

        self.inspector = Inspector()
        layout.addWidget(self.inspector)

    def compose_file_tree(self, root: str) -> QTreeView:
        # TODO: documentação
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

class Inspector(QWidget):
    # TODO: documentação
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.label_title = self.register_value_label('title', layout)
        self.label_type = self.register_value_label('type', layout)
        self.label_id = self.register_value_label('id', layout)
        self.label_created_at = self.register_value_label('created at', layout)
        self.label_fields = self.register_value_label('fields', layout)

    def register_value_label(self, placeholder: str, layout: QHBoxLayout | QVBoxLayout):
        """
        registra um label pra mostrar uma informação no inspector e retorna ele

        args:
            placeholder:
                texto padrão do label

            layout:
                layout em que o label deve ser adicionado
        """

        label = QLabel(placeholder)
        layout.addWidget(label)

        return label

    def open_entry(self, entry: Entry):
        self.label_id.setText(entry.id)
        self.label_type.setText(entry.type)
        self.label_created_at.setText(entry.created_at)
        # TODO: fields
