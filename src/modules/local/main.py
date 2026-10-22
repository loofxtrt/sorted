from ...managers.models import Module, Vault

class LocalModule(Module):
    def __init__(self, vault: Vault):
        super().__init__(id='local', vault=vault)

    