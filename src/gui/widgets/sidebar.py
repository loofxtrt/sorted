import numbers
from pathlib import Path

from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QTreeView
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

        self.form = FieldsForm()
        layout.addWidget(self.form)

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

        self.form.

class FieldsForm(QWidget):
    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)

    # TODO: suporte à sub-dict?
    def register_field(
        self, layout: QFormLayout, label_text: str,
        data_type: type[str] | type[bool] | type[numbers.Number] | None = None
    ) -> QLineEdit | QDoubleSpinBox | QCheckBox | None:
        if isinstance(data_type, str):
            input = QLineEdit()
        elif isinstance(data_type, bool):
            input = QCheckBox()
        elif isinstance(data_type, numbers.Number):
            input = QDoubleSpinBox()
        else:
            input = None

        layout.addRow(label_text, input)

        return input
