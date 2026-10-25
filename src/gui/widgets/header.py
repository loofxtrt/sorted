from PyQt6.QtWidgets import QComboBox, QGroupBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel

from src.gui.widgets.sidebar import GroupedForm
from src.managers.models import Collection


class Header(QWidget):
    """
    cabeçalho da interface, que agrupa o painel de informações e o painel de controles
    """

    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.info_panel = self.compose_info_panel()
        layout.addWidget(self.info_panel)

        self.control_panel = self.compose_control_panel()
        layout.addWidget(self.control_panel)

    def compose_info_panel(self, collection: Collection | None = None) -> QWidget:
        """
        cria o painel de informações da collection

        returns:
            o widget que contém o painel
        """

        form = GroupedForm()

        if not collection:
            return form

        name_label = QLabel(collection.name)
        form.widget_layout.addWidget(name_label)

        form.register_label_row('Entries', str(collection.entry_count))
        form.register_label_row('Created at', collection.created_at)

        return form

#         widget = QWidget()
#         widget_layout = QVBoxLayout(widget)
#         group = QGroupBox('Collection')
#         group_layout = QVBoxLayout(group)
#
#
#         # TODO: func pra atualizar essas labels sem reconstruir tudo
#         # título fica em cima
#         title_label = QLabel(collection.name)
#         group_layout.addWidget(title_label)
#
#         # demais informações ficam em baixo
#         entry_count_label = QLabel(str(collection.entry_count))
#         group_layout.addWidget(entry_count_label)
#
#         # grupo e retorno
#         widget_layout.addWidget(group)
        # return widget

    def compose_control_panel(self) -> QWidget:
        """
        cria o painel de controles
        ex.: input de referece, dropdown de tipo, botões de inserir e remover etc.

        returns:
            o widget que contém o painel
        """

        # self.button_move = QPushButton('Move')
        # self.button_copy = QPushButton('Copy')
        # self.button_edit = QPushButton('Edit')

#         # input de texto + botão pra inserir novas entradas
#         hbox_insert = QHBoxLayout()
#         hbox_insert.addWidget(self.combo_box_type)
#         hbox_insert.addWidget(self.input_insert)
#         hbox_insert.addWidget(self.button_insert)
#
#         vbox_control_panel.addLayout(hbox_insert)
#
#         # row de ações que podem ser tomadas pra cada entrada
        widget = QWidget()
        actions_layout = QHBoxLayout(widget)

        self.input_reference = QLineEdit()
        self.dropdown_type = QComboBox()
        self.button_insert = QPushButton('Insert')
        self.button_remove = QPushButton('Remove')

        actions_layout.addWidget(self.input_reference)
        actions_layout.addWidget(self.dropdown_type)
        actions_layout.addWidget(self.button_insert)
        actions_layout.addWidget(self.button_remove)
#
#         for b in [self.button_remove, self.button_move, self.button_copy]:
#             hbox_actions.addWidget(b)
#
#         vbox_control_panel.addLayout(hbox_actions)

        return widget
