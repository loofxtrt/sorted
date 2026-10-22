from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QAbstractItemView
from pathlib import Path

from src.gui.widgets.header import Header
from src.gui.widgets.sidebar import Sidebar

class Central(QWidget):
    # TODO: documentação
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)

        # horizontal. ex: sidebar -> conteúdo
        layout = QHBoxLayout(self)

        self.sidebar = Sidebar(root=root)
        layout.addWidget(self.sidebar)

        # vertical. ex: header -> central logo embaixo
        self.contents = QWidget()
        self.contents_layout = QVBoxLayout(self.contents)

        self.compose_header()
        self.compose_contents()

        layout.addWidget(self.contents, 1)

    def compose_header(self):
        self.header = Header()
        self.contents_layout.addWidget(self.header)

    def compose_contents(self):
        self.qlist = ContentList() # TODO: mudar qlist pra content_list
        self.contents_layout.addWidget(self.qlist, 1)

class ContentList(QListWidget):
    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # poder selecionar múltiplos itens

    def insert(self, userrole: str, entry_widget: QWidget):
        """
        args:
            userrole:
                dados ocultos que ficam dentro do item na lista
                ex.: IDs

            entry_widget:
                o widget já resolvido e construído da entry
                fornecido pelo módulo responsável pela mesma
        """

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(entry_widget) # TODO: classe entryWidget que contenha tanto o widget quanto a entry

        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, userrole) # inserir os dados ocultos
        item.setSizeHint(container.sizeHint()) # mudar o tamanho do item pra comportar o conteúdo

        # adicionar o item na lista
        self.addItem(item)
        self.setItemWidget(item, container)

    def get_selected_ids(self) -> list[str]:
        # espera que todo item tenha um userrole que indique qual entry ele representa
        items = self.selectedItems()
        return [i.data(Qt.ItemDataRole.UserRole) for i in items]

    def get_current_id(self) -> str | None:
        item = self.currentItem()

        if not item:
            return

        return item.data(Qt.ItemDataRole.UserRole)
