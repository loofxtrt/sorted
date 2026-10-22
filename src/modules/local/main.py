from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from ...managers.models import Module, Vault, Entry

class LocalModule(Module):
    def __init__(self, vault: Vault):
        super().__init__(
            id='local',
            vault=vault,
            supported_types=['file']
        )

    def build_entry_widget(self, entry: Entry) -> QWidget:
        path = Path(entry.reference)

        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        label = QLabel()
        label.setText(path.name)

        layout.addWidget(label)

        return widget
