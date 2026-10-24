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


FAVICON_SIZE = 16 # TODO: fazer ser configurável?


class WebModule(Module):
    # TODO: documentação
    # TODO: documentação de pq plugins core não precisam de manifesto
    # TODO: mais logging
    def __init__(self, vault: Vault):
        super().__init__(
            id='web',
            vault=vault,
            supported_types=['page']
        )

    @property
    def favicons_directoy(self) -> Path:
        """
        retorna o diretório onde os favicons baixados são guardados
        """

        return self.container / 'favicons'

    def get_favicon(self, url: str, size: int=FAVICON_SIZE) -> Path | None:
        """
        obtém o favicon de um site, usando o serviço de favicons do google
        se o favicon já estiver salvo em disco, usa o arquivo existente em vez de baixar de novo

        args:
            url:
                url do site cujo favicon será obtido

            size:
                tamanho do favicon em pixels

        returns:
            o caminho do arquivo do favicon se ele já existia em disco, senão None
        """

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

        # extrai o domínio principal da url e gera a url pra requisitar a api de favicons da google
        domain = tldextract.extract(url).registered_domain
        favicon_via_google = f'https://www.google.com/s2/favicons?domain={domain}&sz={size}'

        # se o favicon desse domínio já foi baixado antes, usa esse mesmo arquivo
        path = self.favicons_directoy / f'{domain}.png'
        if path.exists():
            return path

        try:
            # baixa o favicon via api da google, com um user-agent de navegador pra evitar bloqueio
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url=favicon_via_google, headers=headers, stream=True)
            response.raise_for_status() # levanta um erro se o status for 4xx/5xx

            # salva o arquivo em disco aos poucos (1024 bytes por vez)
            with open(path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            logger.error(f'error while fetching favicon for {url}: {e}')
            return None

        return path

    def build_entry_widget(self, entry: Entry) -> QWidget:
        """
        constrói o widget de uma entry de página web, com o favicon e a url lado a lado

        args:
            entry:
                entry cuja reference é a url da página

        returns:
            o widget construído
        """

        url = entry.reference

        # TODO: fallback
        favicon_file = self.get_favicon(url)
        favicon_pixmap = image_to_pixmap(favicon_file)
        favicon_pixmap = set_pixmap_size(favicon_pixmap, FAVICON_SIZE)
        favicon_label = label_with_pixmap(favicon_pixmap)

        url_label = QLabel(url) # TODO: fazer ser editável aqui também?

        widget = QWidget()
        layout = QHBoxLayout(widget)

        layout.addWidget(favicon_label)
        layout.addWidget(url_label)

        layout.addStretch() # mantém tudo começando da esquerda pra direita

        return widget
