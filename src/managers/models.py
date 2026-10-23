from dataclasses import dataclass
from pathlib import Path

from ..utils.generic import ensure_directory, normalize_json_file
from ..utils import json_io
# from . import VaultCache


# TODO: documentação
class Vault:
    """
    representa um vault de trabalho e gerencia sua estrutura interna

    esta classe cria e organiza o diretório base do vault, incluindo o diretório oculto
    de contexto (.sorted), além de expor caminhos úteis como o diretório de módulos
    e o manifesto, e de registrar os módulos ativos

    args:
        root:
            diretório raiz do vault que será inicializado e garantido no sistema
    """

    def __init__(self, root: Path):
        """
        define e cria o diretório oculto do vault e carrega os módulos listados no manifesto

        root: /path/do/vault
        context: /path/do/vault/.sorted
        manifest: /path/do/vault/.sorted/vault.json
        """

        self.root = root
        ensure_directory(self.root)

        self.context = self.root / '.sorted'
        ensure_directory(self.context)

        self.manifest = self.context / normalize_json_file('vault')

        self.module_registry = ModuleRegistry()
        self.set_modules()

        # self.cache = VaultCache(self.context)

    @property
    def modules_dir(self):
        """
        retorna o diretório de módulos do vault
        cria o diretório caso ainda não exista
        """

        path = self.context / 'modules'
        ensure_directory(path)

        return path

    def set_modules(self):
        """
        lê o manifesto do vault e registra em module_registry os módulos core listados nele
        ids que não existem em CORE_MODULES são ignorados
        """

        from src.managers.maps import CORE_MODULES

        # TODO: fazer mais info no vault.json
        # TODO: por enquanto isso lê apenas módulos core (nativos)
        # TODO: documentação
        data = json_io.read_json(self.manifest)

        module_ids = data.get('modules', {}).get('core', [])
        for id in module_ids:
            module_class = CORE_MODULES.get(id)
            if not module_class:
                continue

            # TODO: quando for ter o externos, identificar os supported types via manifesto
            # enquanto os cores definiriam isso direto no código
            # TODO: módulo nativo não leva id
            self.module_registry.register(module_class(vault=self))

    # TODO: separar um cache pra cada plugin pra n precisar de um dir extra de cache
#     @property
#     def cache_dir(self):
#         """
#         retorna o diretório de cache do vault
#         cria o diretório caso ainda não exista
#         """
#
#         path = self.context / 'cache'
#         ensure_directory(path)
#
#         return path
#
#     @property
#     def cache_file(self):
#         """
#         retorna o arquivo de cache principal do vault
#         """
#
#         return self.context / normalize_json_file('cache')


@dataclass
class Entry:
    """
    representa uma entrada individual dentro de uma collection
    """

    id: str
    created_at: str
    module: str # TODO: talvez teste de remoção completa disso
    type: str
    fields: dict
    reference: str

    @classmethod
    def from_dict(cls, data: dict):
        """
        cria uma entry a partir de um dicionário

        args:
            data:
                dicionário contendo os dados da entry

        returns:
            a entry criada
        """

        return cls(
            id=data.get('id'),
            created_at=data.get('created_at'),
            module=data.get('module'),
            type=data.get('type'),
            reference=data.get('reference'),
            fields=data.get('fields', {})
        )

    def to_dict(self):
        """
        converte a entry em um dicionário, pronto pra ser salvo em json

        returns:
            dicionário com os dados da entry
        """

        return {
            'id': self.id,
            'created_at': self.created_at,
            'module': self.module,
            'type': self.type,
            'reference': self.reference,
            'fields': self.fields
        }


@dataclass
class Collection:
    """
    representa uma collection carregada de um arquivo
    essa estrutura agrupa entries e metadados associados
    """

    id: str
    version: str
    created_at: str
    entries: dict[str, Entry]
    file: Path

    @property
    def name(self):
        """
        retorna o nome da collection
        isso é sempre o nome do arquivo sem a extensão
        """

        return self.file.stem

    @property
    def entry_count(self):
        """
        retorna a quantidade de entradas na collection
        """

        return len(self.entries)

    @classmethod
    def from_dict(cls, data: dict, file: Path):
        """
        cria uma collection a partir de um dicionário

        args:
            data:
                dicionário contendo os dados da collection e suas entries

            file:
                arquivo ao qual a collection pertence, usado depois pra salvar o estado

        returns:
            a collection criada
        """

        entries = { }
        for e in data.get('entries', {}).values():
            entry = Entry.from_dict(e)
            entries[entry.id] = entry

        return cls(
            id=data.get('id'),
            version=data.get('version'),
            created_at=data.get('created_at'),
            entries=entries,
            file=file
        )

    def to_dict(self):
        """
        converte a collection em um dicionário, pronto pra ser salvo em json
        as entries ficam indexadas pelo id

        returns:
            dicionário com os dados da collection e de todas as suas entries
        """

        entries = {}
        for e in self.entries.values():
            entries[e.id] = e.to_dict()

        return {
            'id': self.id,
            'version': self.version,
            'created_at': self.created_at,
            'entries': entries
        }

    @classmethod
    def from_file(cls, file: Path):
        """
        carrega uma collection a partir de um arquivo
        esse arquivo deve ser um json (com extensão .json ou .scol)

        args:
            file:
                caminho do arquivo de collection

        returns:
            a collection carregada
        """

        # TODO: validação mais rigorosa com base na chave type
        data = json_io.read_json(file)
        return cls.from_dict(data, file)

    def write_entry(self, entry: Entry):
        """
        adiciona uma entry na collection, tanto em memória quanto em disco

        args:
            entry:
                entry que será adicionada
                SE JÁ EXISTIR UMA COM O MESMO ID, ELA É SUBSTITUÍDA
        """

        # atualiza a memória primeiro, inserindo a entry nova
        self.entries[entry.id] = entry

        # depois salva no disco
        self.save_state()

    def erase_entry(self, entry_id: str):
        """
        remove uma entry da collection, tanto em memória quanto em disco

        args:
            entry_id:
                id da entry que será removida
        """

        self.entries.pop(entry_id, None)
        self.save_state()

    def save_state(self):
        """
        salva o estado atual da collection em disco
        """

        json_io.write_json(self.file, self.to_dict())



class Module:
    """
    representa um plugin dentro de um vault

    um module é uma extensão isolada do sistema, usada pra adicionar
    funcionalidades específicas (tipo integrações, renderizações, processamento de dados etc)
    sem precisar mexer no core da aplicação

    cada module vive dentro do seu próprio diretório no vault, onde pode guardar arquivos,
    cache, configs e um manifesto com dados persistentes

    a ideia é permitir que funcionalidades sejam plugáveis, removíveis e independentes,
    sem quebrar o resto do sistema

    args:
        id:
            nome único do plugin dentro do vault (ex: "youtube", "core" etc.)

        vault:
            instância do Vault onde esse plugin está rodando

        supported_types:
            tipos de entries que esse módulo lida com
    """

    def __init__(self, id: str, vault: Vault, supported_types: list):
        """
        inicializa o plugin e garante que a estrutura dele existe no disco

        cada module cria uma pasta própria dentro de vault.modules_dir pra armazenar
        dados, cache e arquivos internos
        """

        self.id = id
        self.vault = vault
        self.supported_types = supported_types

        self.root = self.vault.modules_dir / id
        ensure_directory(self.root)

        self.manifest_file = self.root / normalize_json_file('manifest')
        self.manifest_data = self.load_manifest()

    def load_manifest(self):
        """
        carrega o manifesto do plugin

        o manifesto é basicamente um json com infos persistentes do module,
        tipo versão, configs e outros dados que precisam sobreviver entre execuções

        returns:
            dicionário com os dados do manifesto, ou vazio se ainda não existir
        """

        if not self.manifest_file.is_file():
            return {}

        return json_io.read_json(self.manifest_file)

    # TODO
    def build_entry_widget(self, entry: Entry):
        """
        constrói o widget que representa uma entry na interface
        ainda não implementado

        args:
            entry:
                entry cujo widget será construído
        """

        pass

    def can_handle_entry(self, entry: Entry):
        """
        verifica se o módulo sabe lidar com o tipo de uma entry

        args:
            entry:
                entry que será verificada

        returns:
            True se o tipo da entry está em supported_types, senão False
        """

        return entry.type in self.supported_types
#
#     def receive_url(self, url: str):
#         pass



# TODO: documentação
class ModuleRegistry:
    """
    registro dos módulos ativos de um vault
    usado pra descobrir qual módulo sabe lidar com cada entry
    """

    def __init__(self):
        self.modules: list[Module] = []

    def register(self, module):
        """
        adiciona um módulo no registro

        args:
            module:
                módulo que será registrado
        """

        self.modules.append(module)

    def get_entry_compatible_module(self, entry: Entry):
        """
        procura um módulo capaz de lidar com uma entry

        args:
            entry:
                entry pra qual se quer encontrar um módulo

        returns:
            o primeiro módulo registrado que consegue lidar com a entry, ou None se nenhum conseguir
        """

        for m in self.modules:
            if m.can_handle_entry(entry):
                return m

        return None
