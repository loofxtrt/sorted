from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem, QSplitter, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QAbstractItemView
from pathlib import Path

from src.gui.widgets.header import Header
from src.gui.widgets.sidebar import Sidebar

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

class ContentList(QListWidget):
    """
    lista de entries que permite selecionar múltiplos itens
    cada item guarda no UserRole o id da entry que ele representa
    """

    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # poder selecionar múltiplos itens

    def insert(self, userrole: str, entry_widget: QWidget):
        """
        insere uma entry na lista

        args:
            userrole:
                dados ocultos que ficam dentro do item na lista
                ex.: o id da entry que esse item representa

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
