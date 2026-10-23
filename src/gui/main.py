from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QFileDialog, QInputDialog, QComboBox,
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeView, QTabWidget
)
from PyQt6.QtGui import QFileSystemModel, QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from src.gui.widgets.central import Central
from src.gui.widgets.header import Header
from src.gui.widgets.sidebar import Sidebar
from src.managers.controller import get_entry_by_id
from src.modules.local.main import LocalModule

from ..utils.generic import generate_random_id, get_iso_datetime
from ..managers.models import Collection, Vault, Entry, ModuleRegistry
from ..modules.youtube.main import YouTubeModule
from ..modules.youtube.api import extract_video_info, instance_ytdl
from .. import logger


# TODO: documentação
# TODO: mais logging


class Controller:
    def __init__(self, collection: Collection):
        self.collection = collection
        logger.info(f'controller initialized for collection: {self.collection.name}')

    def write_entry(self, module: str, type: str, reference: str):
        logger.info(f'writing entry: module={module}, type={type}, reference={reference}')

        entry = Entry(
            id=generate_random_id(),
            created_at=get_iso_datetime(),
            module=module,
            type=type,
            fields={},
            reference=reference
        )
        self.collection.write_entry(entry)
        logger.success(f'entry written: {entry.id}')

    def erase_entries(self, ids: list[str]):
        logger.info(f'erasing {len(ids)} entr{"y" if len(ids) == 1 else "ies"}')

        for i in ids:
            logger.debug(f'erasing entry: {i}')
            self.collection.erase_entry(i)

        logger.info(f'erased {len(ids)} entr{"y" if len(ids) == 1 else "ies"}')

class MainWindow(QMainWindow):
    def __init__(self, scol: Path, root: Path):
        logger.info(f'initializing main window with collection: {scol}')
        logger.info(f'using vault root: {root}')

        super().__init__()

        self.root = root

        # FIXME: TEMPORÁRIO
        # self.module_registry = ModuleRegistry()
        # self.module_registry.register(YouTubeModule(vault=Vault(root)))
        # self.module_registry.register(LocalModule(vault=Vault(root)))
        self.vault = Vault(self.root)

        # dados e api
        # TODO: .sort em vez de .scol?
        self.scol = scol
        self.collection = Collection.from_file(self.scol)
        logger.info(f'collection loaded: {self.collection.name}')

        self.controller = Controller(self.collection)

        self.central = Central(parent=self, root=self.root)
        self.setCentralWidget(self.central)
        self.load_list_contents() # carregar o conteúdo pela primeira vez. TODO: fazer isso ser uma chamada pra func de mudar o scol, unificando o comportamento?
        self.central.sidebar.file_tree.set_focus(self.scol) # fazer a árvore focar no scol atual

        # registrar todos os tipos disponíveis de entry no vault no dropdown
        # indica o módulo junto de cada tipo, assim como a command palette do obsidian
        for m in self.vault.module_registry.modules:
            for t in m.supported_types:
                display = f'{m.id}:{t}'
                hidden_data = {
                    # dados que ficam ocultos na ui, mas preservados em cada item do dropdown
                    'module': m.id,
                    'type': t
                }

                self.central.header.dropdown_type.addItem(display, hidden_data)

        self.central.qlist.currentItemChanged.connect(self.on_current_entry_changed)
        self.central.header.button_insert.clicked.connect(self.action_insert)
        self.central.header.button_remove.clicked.connect(self.action_remove)

        # inputs
#         self.button_insert = QPushButton('Insert')
#         self.button_remove = QPushButton('Remove')
#         self.button_move = QPushButton('Move')
#         self.button_copy = QPushButton('Copy')
#         self.button_edit = QPushButton('Edit')
#
#         self.button_remove.clicked.connect(self.action_remove)
#         # self.button_insert.clicked.connect(self.action_insert)
#         self.button_move.clicked.connect(self.action_move)

        # TODO
        self.combo_box_type = QComboBox()
        #self.combo_box_type.setCurrentText('youtube.video')

        self.input_insert = QLineEdit()

        # info
        self.label_title = QLabel()
        self.label_entry_count = QLabel()
        self.label_type = QLabel()

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label_title.setFont(font)

        self.load_info_labels()

        # file tree
        # self.root = str(root) # carregar o último root que foi usado
        self.button_root = QPushButton('Change vault')
        self.button_root.clicked.connect(self.action_pick_root)

        self.model = None # tem que ser self pq é importante pra operações com a file tree
        # self.file_tree = self.compose_file_tree()
        self.central.sidebar.file_tree.tree.clicked.connect(self.action_change_collection)

        self.button_create = QPushButton('New collection')
        self.button_create.clicked.connect(self.action_create_collection)

        # widget_sidebar = QWidget()
        # widget_sidebar.setMaximumWidth(350) # é definido no widget inteiro, não só na file tree
        # sidebar = QVBoxLayout(widget_sidebar)

        # sidebar.addWidget(self.file_tree)
        # sidebar.addWidget(self.button_create)
        # sidebar.addWidget(self.button_root)

#     def setup(self):
#         # definir como os contents vão ser exibidos
#         # na ordem vertical, primeiro o barra do topo, depois a lista etc.
#         # widget_contents = QWidget()
#         # contents = QVBoxLayout(widget_contents)
#
#         # LAYOUT
#         ## vertical. ex: header -> central logo embaixo
#         contents = QWidget()
#         contents_layout = (QVBoxLayout(contents))
#
#         self.header = Header()
#         contents_layout.addWidget(self.header)
#
#         ### lista
#         self.qlist = QListWidget()
#         self.qlist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#
#         contents_layout.addWidget(self.qlist, 1)
#
#         self.load_list_contents() # carregar o conteúdo pela primeira vez
#
#         ## horizontal. ex: sidebar -> conteúdo
#         central = QWidget()
#         central_layout = QHBoxLayout(central)
#         self.setCentralWidget(central)
#
#         self.sidebar = Sidebar(root=self.root)
#         central_layout.addWidget(self.sidebar)
#
#         central_layout.addWidget(contents, 1)

#     def compose_file_tree(self) -> QTreeWidget:
#         self.model = QFileSystemModel()
#         self.model.setRootPath(self.root)
#
#         tree = QTreeView()
#         tree.setModel(self.model)
#
#         tree.setRootIndex(self.model.index(self.root))
#
#         tree.setHeaderHidden(True)
#         tree.hideColumn(1)
#         tree.hideColumn(2)
#         tree.hideColumn(3)
#
#         return tree

    def on_current_entry_changed(self):
        """
        identifica o id do item atualmente selecionado
        e abre a entry correspondente no inspector
        """

        current_id = self.central.qlist.get_current_id()
        if not current_id:
            return

        # TODO: esses returns/a falta deles podem falhar silenciosamente. precisa de mais erros

        entry = get_entry_by_id(self.collection, current_id)
        self.central.sidebar.inspector.open_entry(entry)

    def load_list_contents(self):
        logger.debug(f'loading entries for collection: {self.collection.name}')

        self.central.qlist.clear()

        entries = self.collection.entries
        logger.debug(f'found {len(entries)} entries')
        for e in entries.values():
            logger.debug(f'building widget for entry: {e.id}')

            # tenta obter o módulo certo pra lidar com essa entry
            module = self.vault.module_registry.get_entry_compatible_module(e)
            if not module:
                logger.warning(f'no module found for entry: {e.id}')
                continue

            # espera o result em vez de desenpacotar de uma vez
            # pra não quebrar com 'cannot unpack non-iterable NoneType object'
            result = module.build_entry_widget(e)
            if not result:
                logger.warning(f'failed to build widget for entry: {e.id}')
                continue

            # criar o elemento visual da entry
            # TODO: documentação
            # container = QWidget()
            # container_layout = QVBoxLayout()
            # container.setLayout(container_layout)
            # container_layout.addWidget(result)
            # container_layout.addWidget(QLabel(e.id))

            # item = QListWidgetItem()
            # item.setData(Qt.ItemDataRole.UserRole, e.id)
            # item.setSizeHint(container.sizeHint())

            # self.central.qlist.addItem(item)
            # self.central.qlist.setItemWidget(item, container)
            self.central.qlist.insert(userrole=e.id, entry_widget=result)

            # FIXME: temporário
            print('adicionado')

        logger.debug('entry list loaded')

    def load_info_labels(self):
        logger.debug(f'updating collection info: {self.collection.name}')
        logger.debug(f'collection entry count: {self.collection.entry_count}')

        # atualiza os dados exibidos sobre a collection
        self.label_title.setText(self.collection.name)
        self.label_entry_count.setText(str(self.collection.entry_count))

    def refresh(self):
        logger.debug(f'refreshing collection: {self.collection.name}')

        self.load_list_contents()
        self.load_info_labels()

    # def get_selected_ids(self):
    #     # espera que todo item tenha um userrole (valor oculto)
    #     # que indique qual entry ele representa
    #     items = self.central.qlist.selectedItems()
    #     return [i.data(Qt.ItemDataRole.UserRole) for i in items]

    def action_remove(self):
        ids = self.central.qlist.get_selected_ids()
        if not ids:
            logger.warning('remove requested with no entries selected')
            return

        logger.info(f'removing {len(ids)} selected entries')

        self.controller.erase_entries(ids)
        self.refresh()

        logger.success('entries removed and collection refreshed')

    # TODO
    def action_move(self):
        # promptar o caminho novo pra entrada
        dest, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select entry destination',
            filter='json (*.json)'
        )

        if not dest:
            return

        dest = Path(dest)
        if not dest.is_file():
            return

        # se o destino for do mesmo tipo que a collection atual, é uma moção válida
        if utils.file_collection_type_matches('videos', dest):
            ids = self.get_selected_ids()
            for i in ids:
                manager.move_entry(
                    src_collection=self.collection_file,
                    dest_collection=dest,
                    entry_id=i
                )

            self.load_table_contents()

    def action_insert(self):
        # obtém a reference presente no input de texto
        reference = self.central.header.input_reference.text()
        if not reference:
            logger.warning('insert requested with empty input')
            return

        # obtém os dados do dropdown e mapeia o módulo e tipo de acordo
        dropdown_data = self.central.header.dropdown_type.currentData()
        module = dropdown_data.get('module')
        type = dropdown_data.get('type')

        # adiciona na collection e atualiza aa ui
        self.controller.write_entry(module=module, type=type, reference=reference)
        self.refresh()

        # FIXME: TEMPORÁRIO
        # logger.info(f'extracting video information from input: {value}')
        # info = extract_video_info(value, instance_ytdl())

        # if not info:
            # logger.error('failed to extract video information')
            # return

        # self.controller.write_entry(module='youtube', type='video', reference=info.get('id'))
        # self.controller.write_entry(module='local')

    def action_change_collection(self, index):
        # obtém o caminho de um arquivo clicado na file tree
        # e se for uma collection válida e diferente da atual, atualiza a visualização pra ela
        dest = self.central.sidebar.file_tree.model.filePath(index)
        dest = Path(dest)

        if dest == self.collection.file:
            logger.debug(f'clicked collection is the same as the current one: {dest}')
            return

        logger.debug(f'file tree item selected: {dest}')

        #if not dest or not is_collection_valid(dest):
        #    return

        logger.info(f'changing collection: {self.scol} to {dest}')

        self.central.sidebar.file_tree.set_focus(dest)

        self.scol = dest
        self.collection = Collection.from_file(self.scol)
        self.controller = Controller(self.collection) # tbm precisa ser atualizado
        #cache.write_last_collection(dest)

        self.refresh()

        logger.success(f'collection changed to: {dest}')

    # TODO
    def action_change_root(self):
        dest = self.input_root.text()
        if not Path(dest).is_dir():
            return

        self.root = dest
        self.model.setRootPath(self.root)
        self.file_tree.setRootIndex(self.model.index(self.root))

    def action_pick_root(self):
        # define o novo root, o diretório usado pra visualizar
        # quais playlists ele contém
        root = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Pick root'
        )

        if Path(root).is_dir():
            self.root = root
            self.model.setRootPath(root)
            self.file_tree.setRootIndex(self.model.index(root))

        # cache.write_last_root(Path(root))

    def action_create_collection(self):
        text, ok = QInputDialog.getText(
            self,
            'Collection title',
            'Set a title for this collection'
        )

        if ok and text:
            manager.create_collection(
                title=text,
                media_type='videos',
                output_directory=Path(self.root)
            )

def main():
    app = QApplication([])

    # FIXME: nao tem erro se o caminho é inválido
    # FIXME: consertar esse path hardcoded
    # FIXME: temporário
    file = Path('/mnt/seagate/workspace/coding/projetos/software/sorted/testei2/eumerlyteste local.json')
    #file = None

    root = Path('/mnt/seagate/workspace/coding/projetos/software/sorted/testei2')

    main_window = MainWindow(file, root)
    main_window.show()

    app.exec()

main()
