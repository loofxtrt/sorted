import requests

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from pathlib import Path
import favicon
import tldextract

from src.managers.models import Entry, Module, Vault
from src.utils.generic import ensure_directory
from src.utils.qt import image_to_pixmap, label_with_pixmap, set_pixmap_size
from src import logger


class WebModule(Module):
    # TODO: documentação
    # TODO: documentação de pq plugins core não precisam de manifesto
    def __init__(self, vault: Vault):
        super().__init__(
            id='web',
            vault=vault,
            supported_types=['page']
        )

    @property
    def favicons_directoy(self) -> Path:
        return self.container / 'favicons'

    def get_favicon(self, url: str, size: int=32) -> Path | None:
#         icons = favicon.get(url)
#
#         if icons:
#             i = icons[0]
#
#             response = requests.get(i.url, stream=True)
#             filename = tldextract.extract(url).registered_domain
#             path = ensure_directory(self.container / 'favicons' / filename + '.png')
#             with open(filename, 'wb') as f:
#                 for chunk in response.iter_content(1024):
#                     f.write(chunk)
#
#             return

        domain = tldextract.extract(url).registered_domain
        favicon_via_google = f'https://www.google.com/s2/favicons?domain={domain}&sz={size}'

        path = self.favicons_directoy / f'{domain}.png'
        if path.exists():
            return path

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url=favicon_via_google, headers=headers, stream=True)
            response.raise_for_status()

            with open(path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            logger.error(f'error while fetching favicon for {url}: {e}')
            return None

        return None

    def build_entry_widget(self, entry: Entry) -> QWidget:
        url = entry.reference

        # TODO: fallback
        favicon_file = self.get_favicon(url)
        favicon_pixmap = image_to_pixmap(favicon_file)
        favicon_pixmap = set_pixmap_size(favicon_pixmap, 32)
        favicon_label = label_with_pixmap(favicon_pixmap)

        url_label = QLabel(url) # TODO: fazer ser editável aqui também?

        widget = QWidget()
        layout = QHBoxLayout(widget)

        layout.addWidget(favicon_label)
        layout.addWidget(url_label)

        return widget
