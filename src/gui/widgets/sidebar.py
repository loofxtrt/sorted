import numbers
from pathlib import Path

from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLabel, QLineEdit, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QTreeView
from PyQt6.QtGui import QColor, QFileSystemModel, QPalette

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

        self.readonly_form = ReadonlyForm()
        layout.addWidget(self.readonly_form)

        self.fields_form = FieldsForm()
        layout.addWidget(self.fields_form)

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

        self.readonly_form.label_id.setText(entry.id)
        self.readonly_form.label_type.setText(entry.type)
        self.readonly_form.label_created_at.setText(entry.created_at)
        # TODO: fields

        self.fields_form.clear() # limpar o formulário antigo antes de reconstruir

        # obtém os fields que a entry tem e registra cada um
        # com um label pra chave e um input pro valor
        for key, value in entry.fields.items():
            self.fields_form.register_row(key, value)

class GroupedForm(QWidget):
    # TODO: documentação
    def __init__(self, parent=None, group_label: str = ''):
        super().__init__(parent)

        group = QGroupBox(group_label)
        self.form_layout = QFormLayout(group)

        layout = QVBoxLayout(self)
        layout.addWidget(group)
        layout.addStretch() # elementos começam de cima em vez de serem centralizados verticalmente

    def compose_key_label(self, key: str) -> QLabel:
        """
        cria um label padronizado pra ser o rótulo de um row de um formulário
        """

        label = QLabel(key)
        # label.setForegroundRole(QPalette.ColorRole.PlaceholderText) # cor semi-apagada

        # calcular uma cor semi-apagada
        # copiado do código fonte do kde dolphin
        palette = label.palette()
        text = palette.color(QPalette.ColorRole.Base)
        background = palette.color(QPalette.ColorRole.Text)
        factor_1 = 0.2
        factor_2 = 0.8
        secondary = QColor(
            round(text.red() * factor_1 + background.red() * factor_2),
            round(text.green() * factor_1 + background.green() * factor_2),
            round(text.blue() * factor_1 + background.blue() * factor_2)
        )
        palette.setColor(QPalette.ColorRole.WindowText, secondary)
        label.setPalette(palette)

        return label

    def register_row(self, key: str, value: str = '') -> QLabel:
        """
        registra um row no formulário

        args:
            key:
                valor que aparece como chave do row no formulário
                não é igual à chave do json, é só o texto visual do rótulo

            value:
                valor do row

        returns:
            o widget que contém o valor do row
        """

        key_label = self.compose_key_label(key)
        value_label = QLabel(value)

        self.form_layout.addRow(key_label, value_label)

        return value_label

    def clear(self):
        """
        enquanto ainda existir um row presente no formulário, remove ele
        """

        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

class FieldsForm(GroupedForm):
    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent, group_label='Fields')

    # TODO: suporte à sub-dict?
    # TODO: keys editáveis
    def register_row(
        self,
        key: str,
        value: type[str] | type[bool] | type[numbers.Number] | None = None
    ) -> QLineEdit | QDoubleSpinBox | QCheckBox:
        input = QLineEdit()

        if isinstance(value, bool):
            input = QCheckBox()
            input.setChecked(value)
        elif isinstance(value, numbers.Number):
            input = QDoubleSpinBox()
            input.setValue(value)
        else:
            input.setText(str(value))

        # adicionar o input criado no layout e retornar ele
        self.form_layout.addRow(self.compose_key_label(key), input)

        return input

class ReadonlyForm(GroupedForm):
    """
    campo que exibe os valores de uma entry que não são alteráveis pela ui
    """

    def __init__(self, parent=None):
        super().__init__(parent, 'Properties')

        self.label_type = self.register_row('Type')
        self.label_id = self.register_row('ID')
        self.label_created_at = self.register_row('Created at')

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
