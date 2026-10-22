from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout

from src.gui.widgets.header import Header

class Central(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.central = QWidget()
        self.central_layout = QHBoxLayout(self.central)

        # vertical. ex: header -> central logo embaixo
        self.contents = QWidget()
        self.contents_layout = QVBoxLayout(self.contents)

        self.central_layout.addWidget(self.contents, 1)

    def compose_header(self):
        self.header = Header()
        self.contents_layout.addWidget(self.header)

    def compose_contents(self):
        self.qlist = QListWidget()
        self.qlist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.contents_layout.addWidget(self.qlist, 1)

        self.sidebar = Sidebar(root=self.root)
        self.contents_layout.addWidget(self.sidebar)

    # LAYOUT
    ## vertical. ex: header -> central logo embaixo


    ### lista


# 
# 
#     self.load_list_contents() # carregar o conteúdo pela primeira vez
# 
#     ## horizontal. ex: sidebar -> conteúdo
#     central = QWidget()
#     central_layout = QHBoxLayout(central)
#     self.setCentralWidget(central)
# 
# 
#     central_layout.addWidget(self.sidebar)
