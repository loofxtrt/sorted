import numbers
from pathlib import Path

from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLabel, QLineEdit, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QTreeView
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

        # self.file_tree = self.compose_file_tree(str(root))
        self.file_tree = FileTree(root=root)
        layout.addWidget(self.file_tree)

        self.inspector = Inspector()
        layout.addWidget(self.inspector)

#     def compose_file_tree(self, root: str) -> QTreeView:
#         # TODO: documentação
#         self.model = QFileSystemModel()
#         self.model.setRootPath(root)
#
#         tree = QTreeView()
#         tree.setModel(self.model)
#
#         tree.setRootIndex(self.model.index(root))
#
#         tree.setHeaderHidden(True)
#         tree.hideColumn(1)
#         tree.hideColumn(2)
#         tree.hideColumn(3)
#
#         return tree

class Inspector(QWidget):
    # TODO: documentação
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        readonly_group = QGroupBox('Properties')
        readonly_layout = QVBoxLayout(readonly_group)
        # self.label_title = self.register_value_label('title', layout)
        self.label_type = self.register_value_label('type', readonly_layout)
        self.label_id = self.register_value_label('id', readonly_layout)
        self.label_created_at = self.register_value_label('created at', readonly_layout)
        readonly_layout.addStretch()
        layout.addWidget(readonly_group)

        self.form = FieldsForm()
        layout.addWidget(self.form)

        layout.addStretch() # elementos começam de cima em vez de serem centralizados verticalmente

    def register_value_label(self, text: str, layout: QHBoxLayout | QVBoxLayout):
        """
        registra um label pra mostrar uma informação no inspector e retorna ele

        args:
            text:
                texto padrão do label

            layout:
                layout em que o label deve ser adicionado
        """

        label = QLabel(text)
        layout.addWidget(label)

        return label

    def open_entry(self, entry: Entry):
        """
        exibe os dados de uma entry
        """

        self.label_id.setText(entry.id)
        self.label_type.setText(entry.type)
        self.label_created_at.setText(entry.created_at)
        # TODO: fields

        self.form.clear() # limpar o formulário antigo antes de reconstruir

        # obtém os fields que a entry tem e registra cada um
        # com um label pra chave e um input pro valor
        for key, value in entry.fields.items():
            self.form.register_field(key, value)

class FieldsForm(QWidget):
    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        # cria o grupo e um form layout dentro dele
        group = QGroupBox('Fields')
        self.form_layout = QFormLayout(group)

        # adiciona o grupo ao layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(group)
        layout.addStretch()

    # TODO: suporte à sub-dict?
    def register_field(
        self,
        label_text: str,
        data: type[str] | type[bool] | type[numbers.Number] | None = None
    ) -> QLineEdit | QDoubleSpinBox | QCheckBox | None:
        input = QLineEdit()

        if isinstance(data, bool):
            input = QCheckBox()
            input.setChecked(data)
        elif isinstance(data, numbers.Number):
            input = QDoubleSpinBox()
            input.setValue(data)
        else:
            input.setText(str(data))

        # adicionar o input criado no layout e retornar ele
        self.form_layout.addRow(label_text, input)

        return input

    def register_readonly(self, label_text: str, data: str):
        self.form_layout.addRow(label_text, data)

    def clear(self):
        """
        enquanto ainda existir um row presente no formulário, remove ele
        """

        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

class FileTree(QWidget):
    # TODO: documentação
    def __init__(self, root: Path, parent=None):
        super().__init__(parent)

        self.model = QFileSystemModel(self)
        self.model.setRootPath(str(root)) # define a raíz

        self.tree = QTreeView()
        self.tree.setModel(self.model) # define qual model usar
        self.tree.setRootIndex(self.model.index(str(root))) # define a partir de onde a raíz é exibida

        # configurações
        self.tree.setHeaderHidden(True)
        self.tree.hideColumn(1) # tamanho
        self.tree.hideColumn(2) # tipo
        self.tree.hideColumn(3) # data

        # inserção
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)

    def set_focus(self, path: Path):
        """
        foca em um item da árvore caso ele seja válido
        """

        index = self.model.index(str(path))

        if index.isValid():
            self.tree.setCurrentIndex(index)
            self.tree.setFocus() # focar
            # self.tree.scrollTo(index) # scrollar
