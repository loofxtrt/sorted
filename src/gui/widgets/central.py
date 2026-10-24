from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QLabel, QListWidgetItem, QSplitter, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QAbstractItemView
from pathlib import Path

from src.gui.widgets.components import SMALLER_FONT
from src.gui.widgets.header import Header
from src.gui.widgets.sidebar import Sidebar
from src.managers.models import Entry


class Central(QWidget):
    """
    widget central da interface, que agrupa a sidebar e a área de conteúdo

    args:
        root:
            raíz do vault
    """

    # TODO: documentação
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)

        # splitter pra sidebar inteira ser redimensionável
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # horizontal. ex: sidebar -> conteúdo
        self.sidebar = Sidebar(root=root)
        splitter.addWidget(self.sidebar)

        # vertical. ex: header -> central logo embaixo
        self.contents = QWidget()
        self.contents_layout = QVBoxLayout(self.contents)

        self.compose_header()
        self.compose_contents()

        splitter.addWidget(self.contents)

        # adicionar o splitter
        splitter.setSizes([280, 300])
        layout.addWidget(splitter)

    def compose_header(self):
        """
        cria o header e adiciona ele no topo da área de conteúdo
        """

        self.header = Header()
        self.contents_layout.addWidget(self.header)

    def compose_contents(self):
        """
        cria a lista de entries e adiciona ela na área de conteúdo, abaixo do header
        """

        self.qlist = ContentList() # TODO: mudar qlist pra content_list
        self.contents_layout.addWidget(self.qlist, 1)


class EntryWidgetContainer:
    def __init__(self, entry: Entry, entry_widget: QWidget):
        self.entry = entry

        self.inner_container = QWidget()
        self.inner_container_layout = QVBoxLayout(self.inner_container)
        self.inner_container_layout.addWidget(entry_widget)

        self.external_container = QWidget()
        self.external_container_layout = QVBoxLayout(self.external_container)
        self.external_container_layout.addWidget(self.inner_container)
        self.set_style()

        details_label = QLabel(f'{entry.module}:{entry.type}') # TODO: fazer esse tipo:de:formatação via func utilitária
        details_label.setFont(SMALLER_FONT)
        self.external_container_layout.addWidget(details_label)

        self.item = QListWidgetItem()
        self.item.setData(Qt.ItemDataRole.UserRole, self.entry.id) # inserir os dados ocultos # TODO: testar guardando Entry inteira
        # self.item.setSizeHint(self.external_container.sizeHint()) # mudar o tamanho do item pra comportar o conteúdo

        spacing = 10
        hint = self.external_container.sizeHint()
        self.item.setSizeHint(
            QSize(hint.width() + spacing, hint.height() + spacing )
        ) # mudar o tamanho do item pra comportar o conteúdo
        self.external_container_layout.setContentsMargins(0, spacing, 0, spacing)

    def add_to_qlistwidget(self, qlistwidget: QListWidget):
        qlistwidget.addItem(self.item)
        qlistwidget.setItemWidget(self.item, self.external_container)

    def set_style(self):
#         self.inner_container_layout.setContentsMargins(0, 0, 0, 0)
#         self.inner_container_layout.setSpacing(0)
#
#         self.external_container_layout.setContentsMargins(8, 8, 8, 8)
#         self.external_container_layout.setSpacing(4)

        self.external_container.setProperty('class', 'entry')
        self.external_container.setStyleSheet("""
            QWidget[class="entry"] {
                border: 1px solid palette(midlight);
                border-radius: 5px;
                background-color: palette(window);
            }

            QWidget[class="entry"]:hover {
                border-color: palette(highlight)
            }
        """)


class ContentList(QListWidget):
    """
    lista de entries que permite selecionar múltiplos itens
    cada item guarda no UserRole o id da entry que ele representa
    """

    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setSpacing(10)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # poder selecionar múltiplos itens

#     def insert(self, userrole: str, entry_widget: QWidget):
#         """
#         insere uma entry na lista
#
#         args:
#             userrole:
#                 dados ocultos que ficam dentro do item na lista
#                 ex.: o id da entry que esse item representa
#
#             entry_widget:
#                 o widget já resolvido e construído da entry
#                 fornecido pelo módulo responsável pela mesma
#         """
#
#         container = QWidget()
#         container_layout = QVBoxLayout(container)
#         container_layout.addWidget(entry_widget) # TODO: classe entryWidget que contenha tanto o widget quanto a entry
#
#         item = QListWidgetItem()
#         item.setData(Qt.ItemDataRole.UserRole, userrole) # inserir os dados ocultos
#         item.setSizeHint(container.sizeHint()) # mudar o tamanho do item pra comportar o conteúdo
#
#         # adicionar o item na lista
#         self.addItem(item)
#         self.setItemWidget(item, container)

    def insert(self, entry: Entry, entry_widget: QWidget):
        container = EntryWidgetContainer(entry=entry, entry_widget=entry_widget)
        container.add_to_qlistwidget(self)

    def get_selected_ids(self) -> list[str]:
        """
        obtém os ids das entries selecionadas
        espera que todo item tenha um userrole que indique qual entry ele representa

        returns:
            lista com o id de cada item selecionado
        """

        # espera que todo item tenha um userrole que indique qual entry ele representa
        items = self.selectedItems()
        return [i.data(Qt.ItemDataRole.UserRole) for i in items]

    def get_current_id(self) -> str | None:
        """
        obtém o id da entry do item atual

        returns:
            o id do item atual, ou None se não houver nenhum
        """

        item = self.currentItem()

        if not item:
            return

        return item.data(Qt.ItemDataRole.UserRole)
