from pathlib import Path
import numbers

from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QTreeView
from PyQt6.QtGui import QColor, QFileSystemModel, QPalette
from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal

from src.gui.widgets.components import TagWindow
from src.managers.models import Entry

class Sidebar(QWidget):
    """
    container principal da interface lateral, que agrupa a árvore de arquivos e o inspector

    args:
        root:
            raíz do vault
    """

    # TODO: documentação
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)

        # splitter pra cada painél ser redimensionável
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # self.entry_widget = QWidget()
        # splitter.addWidget(self.entry_widget)

        # árvore de arquivos
        # self.file_tree = self.compose_file_tree(str(root))
        self.file_tree = FileTree(root=root)
        splitter.addWidget(self.file_tree)

        # inspetor de entries
        self.inspector = Inspector()
        splitter.addWidget(self.inspector)

        # adicionar o splitter
        splitter.setSizes([250, 250])
        layout.addWidget(splitter)

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
    """
    painel que exibe as informações de uma entry aberta, dividido em um formulário
    somente leitura (ReadonlyForm) e um formulário de fields editáveis (FieldsForm)
    """

    # TODO: documentação
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.metadata_form = MetadataForm()
        layout.addWidget(self.metadata_form)

        # TODO
        # fields_container = QWidget()
        # fields_container_layout = QVBoxLayout(fields_container)
        # self.fields_form = FieldsForm()
        # fields_container_layout.addWidget(self.fields_form)
        # layout.addWidget(fields_container)
        self.fields_form = FieldsForm()
        layout.addWidget(self.fields_form)

        layout.addStretch() # elementos começam de cima em vez de serem centralizados verticalmente

    def open_entry(self, entry: Entry):
        """
        exibe os dados de uma entry

        args:
            entry:
                entry cujos dados serão exibidos nos formulários
        """

        # atualizar os labels que exibem os dados
        self.metadata_form.label_id.setText(entry.id)
        self.metadata_form.label_type.setText(entry.type)
        self.metadata_form.label_created_at.setText(entry.created_at)
        self.metadata_form.input_reference.setText(entry.reference)

        self.fields_form.clear() # limpar o formulário antigo antes de reconstruir

        # obtém os fields que a entry tem e registra cada um
        # com um label pra chave e um input pro valor
        for key, value in entry.fields.items():
            self.fields_form.register_input_row(key, value)

        # botão de field novo
        self.fields_form.register_button_row('New field')

class GroupedForm(QWidget):
    """
    formulário de pares chave/valor envolvido por um QGroupBox

    args:
        group_label:
            título exibido no topo do grupo

    signals:
        input_row_changed:
            emitido quando o valor de um input muda, com a chave do field e o novo valor
    """

    input_row_changed = pyqtSignal(str, object)

    # TODO: documentação
    def __init__(self, parent=None, group_label: str = ''):
        super().__init__(parent)

        self.group = QGroupBox(group_label)
        self.group_layout = QVBoxLayout(self.group)

        self.form_layout = QFormLayout()
        self.group_layout.addLayout(self.form_layout)

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(self.group)
        self.widget_layout.addStretch() # elementos começam de cima em vez de serem centralizados verticalmente

        self.windows = {}

    def _compose_key_label(self, key: str) -> QLabel:
        """
        cria um label padronizado pra ser o rótulo de um row de um formulário

        returns:
            o label criado
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

        color = QColor(
            round(text.red() * factor_1 + background.red() * factor_2),
            round(text.green() * factor_1 + background.green() * factor_2),
            round(text.blue() * factor_1 + background.blue() * factor_2)
        )

        palette.setColor(QPalette.ColorRole.WindowText, color)
        label.setPalette(palette)

        # retornar o label criado
        return label

    def register_label_row(self, key: str, value: str | QLabel = '') -> QLabel:
        """
        registra um row de label no formulário

        args:
            key:
                valor que aparece como chave do row no formulário
                não é igual à chave do json, é só o texto visual do rótulo

            value:
                valor do row como string ou qlabel pronta

        returns:
            o widget que contém o valor do row
        """

        key_label = self._compose_key_label(key)

        if isinstance(value, QLabel):
            value_label = value
        else:
            value_label = QLabel(value)

        self.form_layout.addRow(key_label, value_label)

        return value_label

    def register_input_row(
        self,
        key: str,
        value: type[str] | type[bool] | type[numbers.Number] | type[list] | None = None
    ) -> QLineEdit | QDoubleSpinBox | QCheckBox:
        """
        registra um row editável no formulário
        o tipo do input é escolhido a partir do tipo de value:
            - bool vira QCheckBox
            - número vira QDoubleSpinBox
            - o resto vira QLineEdit

        args:
            value:
                valor inicial do input

        returns:
            o input criado pro row
        """

        input = QLineEdit()
        input_row_changed_callback = lambda v, k=key: self.input_row_changed.emit(k, v)

        # TODO: documentação
        if isinstance(value, bool):
            input = QCheckBox()
            input.setChecked(value)

            input.toggled.connect(input_row_changed_callback)
        elif isinstance(value, numbers.Number):
            input = QDoubleSpinBox()
            input.setValue(value)

            input.valueChanged.connect(input_row_changed_callback)
        elif isinstance(value, list):
            # inspirado no sistema de edição de tags do kde dolphin
            # TODO: fazer uma versão melhorada inspirada nas tags do obsidian
            # TODO: documentação
            if key not in self.windows:
                self.windows[key] = TagWindow()

            window = self.windows[key]

            input = QPushButton('Edit')
            input.clicked.connect(window.show)
        else:
            if value is not None:
                input.setText(str(value))
            else:
                input.setText('')

            input.textEdited.connect(input_row_changed_callback)

        # adicionar o input criado no layout e retornar ele
        self.form_layout.addRow(self._compose_key_label(key), input)

        return input

    def register_button_row(self, text: str):
        # TODO: documentação
        self.form_layout.addRow(QPushButton(text))

    def clear(self):
        """
        enquanto ainda existir um row presente no formulário, remove ele
        """

        # TODO: documentação
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

class MetadataForm(GroupedForm):
    # TODO: documentação
    def __init__(self, parent=None, group_label: str = 'Metadata'):
        super().__init__(parent, group_label)

        self.label_type = self.register_label_row('Type')
        self.label_id = self.register_label_row('ID')
        self.label_created_at = self.register_label_row('Created at')
        self.input_reference = self.register_input_row('Reference')

class FieldsForm(GroupedForm):
    # TODO: documentação
    def __init__(self, parent=None, group_label: str = 'Fields'):
        super().__init__(parent, group_label)

class FileTree(QWidget):
    """
    árvore de arquivos baseada em QFileSystemModel, com apenas a coluna de nome visível
    """

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

        args:
            path:
                caminho do item que deve ser focado
        """

        index = self.model.index(str(path))

        if index.isValid():
            self.tree.setCurrentIndex(index)
            self.tree.setFocus() # focar
            # self.tree.scrollTo(index) # scrollar
