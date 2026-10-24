from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QListWidgetItem, QSplitter, QStyledItemDelegate, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QAbstractItemView
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
    """
    envolve o widget de uma entry com o estilo e os detalhes usados na lista
    cria também o item da lista, que guarda no UserRole o id da entry

    args:
        entry:
            entry representada pelo container

        entry_widget:
            o widget já resolvido e construído da entry
            fornecido pelo módulo responsável pela mesma
    """

    def __init__(self, entry: Entry, entry_widget: QWidget):
        self.entry = entry

        # container interno: envolve o widget da entry fornecido pelo módulo
        self.inner_container = QWidget()
        self.inner_container_layout = QVBoxLayout(self.inner_container)
        self.inner_container_layout.addWidget(entry_widget)

        # container externo: recebe o container interno e é quem recebe o estilo (borda, fundo etc.)
        self.external_container = QWidget()
        self.external_container_layout = QVBoxLayout(self.external_container)
        self.external_container_layout.addWidget(self.inner_container)
        self.set_style()

        # detalhes: mostra detalhes como o módulo e o tipo da entry embaixo do widget
        details_label = QLabel(f'{entry.module}:{entry.type}') # TODO: fazer esse tipo:de:formatação via func utilitária
        details_label.setFont(SMALLER_FONT)
        self.external_container_layout.addWidget(details_label)

        # item da lista: guarda o id da entry e o tamanho necessário pra comportar o conteúdo
        self.item = QListWidgetItem()
        self.item.setData(Qt.ItemDataRole.UserRole, self.entry.id) # inserir os dados ocultos # TODO: testar guardando Entry inteira
        self.item.setSizeHint(self.external_container.sizeHint()) # mudar o tamanho do item pra comportar o conteúdo

    def add_to_qlistwidget(self, qlistwidget: QListWidget):
        """
        adiciona o item da entry em uma lista e associa o widget do container a ele

        args:
            qlistwidget:
                lista em que o item será adicionado
        """

        qlistwidget.addItem(self.item)
        qlistwidget.setItemWidget(self.item, self.external_container)

    def set_style(self):
        """
        aplica o estilo do container externo: borda, fundo, cor de hover etc.
        """

        self.external_container.setProperty('class', 'entry') # adicionar a classe
        self.external_container.setStyleSheet("""
            QWidget[class="entry"] {
                border: 1px solid palette(midlight);
                border-radius: 5px;
                background-color: palette(window);
            }

            QWidget[class="entry"]:hover {
                background-color: palette(midlight);
            }

            QWidget[class="entry"][selected="true"] {
                border-color: palette(highlight);
            }
        """)


class ContentList(QListWidget):
    """
    lista de entries que permite selecionar múltiplos itens
    cada item guarda no UserRole o id da entry que ele representa

    o estilo de seleção é aplicado nos widgets dos itens, não nos itens em si
    """

    # TODO: documentação
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # poder selecionar múltiplos itens
        self.itemSelectionChanged.connect(self._update_selection_style)

        # define um espaçamento, o que faz com que o bg padrão de seleção não funcione direito
        # então força todos esses estados padrão de seleção ficarem ocultos, se encarregando de gerenciar eles depois
        # FIXME: ainda tem alguns casos que aparecem. tipo seleção -> lmb + ctrl nessa mesma seleçãos
        self.setSpacing(10)
        self.setStyleSheet("""
            QListWidget::item:hover,
                QListWidget::item:selected,
                QListWidget::item:selected:hover,
                QListWidget::item:selected:!active {
                background: transparent;
                outline: none;
            }
        """)

    def _update_selection_style(self):
        """
        atualiza a propriedade selected do widget de cada item de acordo com a seleção atual
        isso reaplica o estilo, fazendo a borda de destaque aparecer só nos itens selecionados
        """

        # percorre todos os itens da lista
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)

            # ignora itens que ainda não tiverem widget associado
            if widget is None:
                continue

            # marca no widget se o item está selecionado, pro stylesheet poder usar [selected="true"]
            widget.setProperty('selected', item.isSelected())

            # força o qt a reaplicar o estilo, senão a mudança da propriedade não aparece
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def insert(self, entry: Entry, entry_widget: QWidget):
        """
        insere uma entry na lista

        args:
            entry:
                entry que será adicionada

            entry_widget:
                o widget já resolvido e construído da entry
                fornecido pelo módulo responsável pela mesma
        """

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
