from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from src.managers.models import Entry


class TagWindow(QWidget):
    # TODO
    # TODO: documentação
    def __init__(self, entry: Entry, parent = None) -> None:
        super().__init__(parent)

        self.setWindowTitle('Tags')
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        layout.addWidget(content)

        self.tag_list = QListWidget()
        for t in entry.fields.get('tags', []):
            self.register_tag_item(str(t))

        controls = QWidget()
        controls_layout = QVBoxLayout(controls)

        create_tag = QWidget()
        create_tag_layout = QHBoxLayout(create_tag)
        self.button_create_tag = QPushButton('+')
        self.input_create_tag = QLineEdit()
        create_tag_layout.addWidget(self.input_create_tag)
        create_tag_layout.addWidget(self.button_create_tag)
        self._register_widget_item(create_tag)
        self.button_create_tag.clicked.connect(lambda: self.action_create_tag(self.input_create_tag.text(), entry))

#         actions = QWidget()
#         actions_layout = QHBoxLayout(actions)
#
#         self.button_cancel = QPushButton('Cancel')
#         actions_layout.addWidget(self.button_cancel)
#
#         self.button_save = QPushButton('Save')
#         actions_layout.addWidget(self.button_save)

        controls_layout.addWidget(create_tag)
        # controls_layout.addWidget(actions)

        content_layout.addWidget(self.tag_list)
        content_layout.addWidget(controls)

    def _register_widget_item(self, widget: QWidget):
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())

        self.tag_list.addItem(item)
        self.tag_list.setItemWidget(item, widget)

    def register_tag_item(self, tag: str):
        tag_widget = QWidget()
        tag_layout = QHBoxLayout(tag_widget)

        tag_layout.addWidget(QCheckBox())
        tag_layout.addWidget(QLabel(tag))

        self._register_widget_item(tag_widget)

    def action_create_tag(self, tag: str, entry: Entry):
        tags = entry.fields.get('tags', [])
        tags.append(tag)
        entry.fields['tags'] = tags
        self.register_tag_item(tag) # memória. TODO: decidir se isso ou recarregar o do disco
        # TODO: collection save state
        # TODO: remover item vazio no inicio
        # TODO: segurança de tags repetidas

def build_error_entry_widget(main_text: str = 'Entry not found', details_text: str | None = None) -> QWidget:
    """
    cria um widget de erro pra ser exibido no lugar de uma entry que não pôde ser construída
    o widget tem um texto principal, um texto de detalhes opcional e um fundo em degradê vermelho

    args:
        main_text:
            texto principal, exibido em fonte maior

        details_text:
            texto secundário exibido abaixo do principal
            se for None, nenhum texto de detalhes é exibido

    returns:
        o widget de erro
    """

    widget = QWidget()
    layout = QVBoxLayout(widget)

    # texto principal
    # main_font = QFont()
    # main_font.setPointSize(14)
    # main_font.setBold(True)

    main_label = QLabel(main_text)
    main_label.setFont(BIGGER_FONT)

    layout.addWidget(main_label)

    # adicionar detalhes (caso especificado)
    if details_text:
        layout.addWidget(QLabel(details_text))

    # elementos começam de cima em vez de serem centralizados verticalmente
    layout.addStretch()

    # estilo (gradiente vermelho que some da esquerda pra direita)
    widget.setObjectName('error_entry')
    widget.setStyleSheet("""
        QWidget#error_entry {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(220, 50, 50, 65),
                stop: 0.15 rgba(220, 50, 50, 25),
                stop: 0.4 rgba(220, 50, 50, 0),
                stop: 1 rgba(220, 50, 50, 0)
            );
        }
    """)

    return widget


# TODO: tamanho de fonte base específico (ex.: 10)

SMALLER_FONT = QFont()
SMALLER_FONT.setPointSize(8)

BIGGER_FONT = QFont()
BIGGER_FONT.setPointSize(14)
