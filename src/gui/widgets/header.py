from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

class Header(QWidget):
    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.info_panel = self.compose_info_panel()
        layout.addWidget(self.info_panel)

        self.control_panel = self.compose_control_panel()
        layout.addWidget(self.control_panel)

    def compose_info_panel(self) -> QWidget:
        widget = QWidget()

        # título fica em cima
        title_label = QLabel('title')

        layout = QVBoxLayout(widget)
        layout.addWidget(title_label)

        # demais informações ficam em baixo
        entry_count_label = QLabel('information')
        layout.addWidget(entry_count_label)

        return widget

    def compose_control_panel(self) -> QWidget:
        widget = QWidget()

#         # input de texto + botão pra inserir novas entradas
#         hbox_insert = QHBoxLayout()
#         hbox_insert.addWidget(self.combo_box_type)
#         hbox_insert.addWidget(self.input_insert)
#         hbox_insert.addWidget(self.button_insert)
#
#         vbox_control_panel.addLayout(hbox_insert)
#
#         # row de ações que podem ser tomadas pra cada entrada
#         hbox_actions = QHBoxLayout()
#
#         for b in [self.button_remove, self.button_move, self.button_copy]:
#             hbox_actions.addWidget(b)
#
#         vbox_control_panel.addLayout(hbox_actions)

        return widget
