import requests

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from pathlib import Path
import favicon
import tldextract

from src.managers.models import Entry, Module, Vault
from src.utils.generic import ensure_directory


class WebModule(Module):
    # TODO: documentação
    # TODO: documentação de pq plugins core não precisam de manifesto
    def __init__(self, vault: Vault):
        super().__init__(
            id='web',
            vault=vault,
            supported_types=['page']
        )

    def get_favicon(self, url: str) -> Path | None:
        icons = favicon.get(url)

        if icons:
            i = icons[0]

            response = requests.get(i.url, stream=True)
            filename = tldextract.extract(url).registered_domain
            path = ensure_directory(self.container / 'favicons' / filename + '.png')
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return

        return None

    def build_entry_widget(self, entry: Entry) -> QWidget:
        favicon_pixmap = QPixmap()

        favicon_label = QLabel()
        favicon_label.setPixmap(favicon_pixmap)

        url_label = QLabel(entry.reference) # TODO: fazer ser editável aqui também?

        widget = QWidget()
        layout = QHBoxLayout(widget)

        layout.addWidget(favicon_label)
        layout.addWidget(url_label)

        return widget
