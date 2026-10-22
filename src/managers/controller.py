from src.managers.models import Collection, Entry

def get_entry_by_id(collection: Collection, id: str) -> Entry | None:
    """
    pesquisa uma entry com um id específico dentro de uma collection
    """

    return collection.entries[id]
