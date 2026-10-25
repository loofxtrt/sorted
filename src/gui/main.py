from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QFileDialog, QInputDialog, QComboBox,
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeView, QTabWidget
)
from PyQt6.QtGui import QFileSystemModel, QFont, QIcon, QKeySequence, QPixmap, QShortcut
from PyQt6.QtCore import Qt, QSize

from src.gui.widgets.central import Central
from src.gui.widgets.components import build_error_entry_widget
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
    """
    intermedia as operações sobre uma collection, registrando logs de cada ação

    args:
        collection:
            collection que será manipulada pelo controller
    """

    def __init__(self, collection: Collection):
        self.collection = collection
        logger.info(f'controller initialized for collection: {self.collection.name}')

    def write_entry(self, module: str, type: str, reference: str):
        """
        cria uma entry nova e adiciona ela na collection
        o id e a data de criação são gerados automaticamente, e os fields começam vazios

        args:
            module:
                id do módulo responsável pela entry

            type:
                tipo da entry

            reference:
                reference da entry (ex.: url ou caminho)
        """

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
        """
        remove várias entries da collection

        args:
            ids:
                ids das entries que serão removidas
        """

        logger.info(f'erasing {len(ids)} entr{"y" if len(ids) == 1 else "ies"}')

        for i in ids:
            logger.debug(f'erasing entry: {i}')
            self.collection.erase_entry(i)

        logger.info(f'erased {len(ids)} entr{"y" if len(ids) == 1 else "ies"}')

    def write_fields(self, entry: Entry, key: str, value: object):
        """
        atualiza o valor de um field de uma entry e salva o estado da collection em disco

        args:
            entry:
                entry cujo field será atualizado

            key:
                chave do field que será atualizado (se não existir, é criado)

            value:
                novo valor do field
        """

        entry.fields[key] = value
        self.collection.save_state()

        logger.success(f'fields updated: {entry.id}')

    def write_metadata(self, entry: Entry, key: str, value: object):
        """
        atualiza um metadata editável da entry e salva o estado da collection em disco

        ESSAS KEYS SÃO AS KEYS VISUAIS, NÃO AS DO JSON
        SE A LABEL DE UM INPUT MOSTRAR 'Reference' PROCURAR POR 'reference' AQUI NÃO FUNCIONA

        args:
            entry:
                entry cujo metadata será atualizado

            key:
                key visual do metadata que será atualizado (ex.: 'Reference')
                keys não reconhecidas são ignoradas

            value:
                novo valor do metadata
        """

        if key == 'Reference':
            entry.reference = str(value)

        self.collection.save_state()

        logger.success(f'metadata updated: {entry.id}')


class MainWindow(QMainWindow):
    """
    janela principal da aplicação, que liga a interface, o vault e a collection aberta

    args:
        scol:
            arquivo da collection que será aberta ao iniciar

        root:
            raíz do vault
    """

    def __init__(self, scol: Path, root: Path):
        logger.info(f'initializing main window with collection: {scol}')
        logger.info(f'using vault root: {root}')

        super().__init__()

        self.root = root
        self.vault = Vault(self.root)

        # dados e api
        # TODO: .sort em vez de .scol?
        self.scol = scol
        self.collection = Collection.from_file(self.scol)
        logger.info(f'collection loaded: {self.collection.name}')

        self.controller = Controller(self.collection)

        # construção da ui
        self.central = Central(parent=self, root=self.root)
        self.setCentralWidget(self.central)

        self.load_list_contents() # carregar o conteúdo pela primeira vez. TODO: fazer isso ser uma chamada pra func de mudar o scol, unificando o comportamento?
        self.central.sidebar.file_tree.set_focus(self.scol) # fazer a árvore focar no scol atual
        self.central.header.update_info_panel(self.collection) # TODO: se o change collection fosse chamado no início em vez disso, não precisaria da duplicação

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

        # conexões
        self.central.qlist.currentItemChanged.connect(self.on_current_entry_changed)
        self.central.header.button_insert.clicked.connect(self.action_insert)
        self.central.header.button_remove.clicked.connect(self.action_remove)
        self.central.sidebar.inspector.fields_form.input_row_changed.connect(self.on_fields_changed)
        self.central.sidebar.inspector.metadata_form.input_row_changed.connect(self.on_metadata_changed)

        # file tree
        self.model = None # tem que ser self pq é importante pra operações com a file tree
        self.central.sidebar.file_tree.tree.clicked.connect(self.action_change_collection)

        # shortcuts
        shortcut = QShortcut(QKeySequence.StandardKey.Delete, self.central.qlist)
        shortcut.activated.connect(self.action_remove)

        # info
#         self.label_title = QLabel()
#         self.label_entry_count = QLabel()
#         self.label_type = QLabel()
#
#         font = QFont()
#         font.setPointSize(16)
#         font.setBold(True)
#         self.label_title.setFont(font)

        # self.root = str(root) # carregar o último root que foi usado
        # self.button_root = QPushButton('Change vault')
        # self.button_root.clicked.connect(self.action_pick_root)

        # self.file_tree = self.compose_file_tree()
#
#         self.button_create = QPushButton('New collection')
#         self.button_create.clicked.connect(self.action_create_collection)

    def get_currenty_entry(self) -> Entry | None:
        """
        identifica a entry atualmente selecionada

        returns:
            a entry do item atual da lista, ou None se não houver nenhum item atual
        """

        # identifica o id do item selecionado
        current_id = self.central.qlist.get_current_id()
        if not current_id:
            return

        # TODO: esses returns/a falta deles podem falhar silenciosamente. precisa de mais erros

        # retorna o resultado da busca de uma entry com esse id
        return get_entry_by_id(self.collection, current_id)

    def on_current_entry_changed(self):
        """
        abre a entry atual no inspector
        não faz nada se não houver entry atual
        """

        entry = self.get_currenty_entry()

        # TODO: esses returns/a falta deles podem falhar silenciosamente. precisa de mais erros
        if not entry:
            return

        self.central.sidebar.inspector.open_entry(entry)

    def on_fields_changed(self, key: str, value: object):
        """
        repassa pro controller a alteração de um field da entry atual
        não faz nada se não houver entry atual

        args:
            key:
                chave do field que foi alterado

            value:
                novo valor do field
        """

        entry = self.get_currenty_entry()

        # TODO: esses returns/a falta deles podem falhar silenciosamente. precisa de mais erros
        if not entry:
            return

        self.controller.write_fields(entry=entry, key=key, value=value)

    def on_metadata_changed(self, key: str, value: object):
        """
        repassa pro controller a alteração de um metadata da entry atual
        não faz nada se não houver entry atual

        args:
            key:
                key visual do metadata que foi alterado

            value:
                novo valor do metadata
        """

        entry = self.get_currenty_entry()

        # TODO: esses returns/a falta deles podem falhar silenciosamente. precisa de mais erros
        if not entry:
            return

        self.controller.write_metadata(entry=entry, key=key, value=value)

    def load_list_contents(self):
        """
        limpa a lista e reconstrói o widget de cada entry da collection
        entries sem módulo compatível, ou cujo widget falhe ao ser construído, recebem um widget de erro
        """

        logger.debug(f'loading entries for collection: {self.collection.name}')

        self.central.qlist.clear() # limpar a lista antes de reconstruir

        entries = self.collection.entries
        logger.debug(f'found {len(entries)} entries')

        for e in entries.values():
            logger.debug(f'building widget for entry: {e.id}')

            # tenta obter o módulo certo pra lidar com essa entry
            module = self.vault.module_registry.get_entry_compatible_module(e)
            if not module:
                logger.warning(f'no module found for entry: {e.id}')
                result = build_error_entry_widget(details_text=f'No module with ID \'{e.module}\' found to handle \'{e.id}\'. Type: \'{e.type}\'')
            else:
                # espera o result em vez de desenpacotar de uma vez
                # pra não quebrar com 'cannot unpack non-iterable NoneType object'
                result = module.build_entry_widget(e)

                if not result:
                    logger.warning(f'failed to build widget for entry: {e.id}')
                    result = build_error_entry_widget(details_text=f'Failed to build widget for \'{e.id}\'')

            # criar o elemento visual da entry
            # cores de borda: midlight/shadow
            # cores de fundo: window
            # FIXME: especificar o estilo aqui, quebra o estilo do widget de erro
#             result.setProperty('class', 'entry')
#             result.setStyleSheet("""
#                 QWidget[class="entry"] {
#                     border: 1px solid palette(midlight);
#                     border-radius: 5px;
#                     background-color: palette(window);
#                 }
#
#                 QWidget[class="entry"]:hover {
#                     border-color: palette(highlight)
#                 }
#             """)
#             result.setStyleSheet("""
#                 QWidget[class="entry"] {
#                     border: 1px solid palette(midlight);
#                     border-radius: 5px;
#
#                 }
#             """)
            # self.central.qlist.insert(userrole=e.id, entry_widget=result)
            self.central.qlist.insert(entry=e, entry_widget=result)

            logger.success(f'entry builded as widget: {e.id}')

        logger.debug('entry list loaded')

    def refresh(self):
        """
        recarrega o conteúdo da lista a partir da collection atual
        """

        logger.debug(f'refreshing collection: {self.collection.name}')

        self.load_list_contents()

    def action_remove(self):
        """
        remove as entries selecionadas na lista e atualiza a ui
        não faz nada se não houver entries selecionadas
        """

        ids = self.central.qlist.get_selected_ids()
        if not ids:
            logger.warning('remove requested with no entries selected')
            return

        logger.info(f'removing {len(ids)} selected entries')

        self.controller.erase_entries(ids)
        self.refresh()

        logger.success('entries removed and collection refreshed')

    # TODO
#     def action_move(self):
#         # promptar o caminho novo pra entrada
#         dest, _ = QFileDialog.getOpenFileName(
#             parent=self,
#             caption='Select entry destination',
#             filter='json (*.json)'
#         )
#
#         if not dest:
#             return
#
#         dest = Path(dest)
#         if not dest.is_file():
#             return
#
#         # se o destino for do mesmo tipo que a collection atual, é uma moção válida
#         if utils.file_collection_type_matches('videos', dest):
#             ids = self.get_selected_ids()
#             for i in ids:
#                 manager.move_entry(
#                     src_collection=self.collection_file,
#                     dest_collection=dest,
#                     entry_id=i
#                 )
#
#             self.load_table_contents()

    def action_insert(self):
        """
        cria uma entry com a reference digitada no input e o módulo/tipo escolhido no dropdown
        depois atualiza a ui
        não faz nada se o input estiver vazio
        """

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

    # TODO
    def action_change_collection(self, index):
        """
        troca a collection aberta pela do item clicado na file tree
        o controller também é recriado e a ui é atualizada
        não faz nada se o item clicado for a collection atual

        args:
            index:
                índice do item clicado na file tree
        """

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
        self.central.header.update_info_panel(self.collection) # atualizar o paínel de informações

        self.refresh()

        logger.success(f'collection changed to: {dest}')
#
#     # TODO
#     def action_change_root(self):
#         dest = self.input_root.text()
#         if not Path(dest).is_dir():
#             return
#
#         self.root = dest
#         self.model.setRootPath(self.root)
#         self.file_tree.setRootIndex(self.model.index(self.root))
#
#     def action_pick_root(self):
#         # define o novo root, o diretório usado pra visualizar
#         # quais playlists ele contém
#         root = QFileDialog.getExistingDirectory(
#             parent=self,
#             caption='Pick root'
#         )
#
#         if Path(root).is_dir():
#             self.root = root
#             self.model.setRootPath(root)
#             self.file_tree.setRootIndex(self.model.index(root))
#
#         # cache.write_last_root(Path(root))
#
#     def action_create_collection(self):
#         text, ok = QInputDialog.getText(
#             self,
#             'Collection title',
#             'Set a title for this collection'
#         )
#
#         if ok and text:
#             manager.create_collection(
#                 title=text,
#                 media_type='videos',
#                 output_directory=Path(self.root)
#             )

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
