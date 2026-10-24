from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


def set_secondary_text_palette(source_widget: QWidget):
    palette = source_widget.palette()

    # calcular uma cor semi-apagada
    # copiado do código fonte do kde dolphin
    text = palette.color(QPalette.ColorRole.Text)
    background = palette.color(QPalette.ColorRole.Base)

    factor_1 = 0.2
    factor_2 = 0.8

    secondary = QColor(
        round(text.red() * factor_1 + background.red() * factor_2),
        round(text.green() * factor_1 + background.green() * factor_2),
        round(text.blue() * factor_1 + background.blue() * factor_2)
    )

    # definir a cor na paleta
    palette.setColor(QPalette.ColorRole.WindowText, secondary)
    source_widget.setPalette(palette)

def build_error_entry_widget(main_text: str = 'Entry not found', details_text: str | None = None) -> QWidget:
    """
    cria um widget de erro pra ser exibido no lugar de uma entry que não pôde ser construída
    o widget tem um texto principal, um texto de detalhes opcional e um fundo em degradê vermelho

    args:
        main_text:
            texto principal, exibido em fonte maior

        details_text:
            texto secundário exibido abaixo do principal
            se for None, nenhum texto de detalhes é exibido

    returns:
        o widget de erro
    """

    widget = QWidget()
    layout = QVBoxLayout(widget)

    # texto principal
    # main_font = QFont()
    # main_font.setPointSize(14)
    # main_font.setBold(True)

    main_label = QLabel(main_text)
    main_label.setFont(BIGGER_FONT)

    layout.addWidget(main_label)

    # adicionar detalhes (caso especificado)
    if details_text:
        layout.addWidget(QLabel(details_text))

    # elementos começam de cima em vez de serem centralizados verticalmente
    layout.addStretch()

    # estilo (gradiente vermelho que some da esquerda pra direita)
    widget.setObjectName('error_entry')
    widget.setStyleSheet("""
        QWidget#error_entry {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(220, 50, 50, 65),
                stop: 0.15 rgba(220, 50, 50, 25),
                stop: 0.4 rgba(220, 50, 50, 0),
                stop: 1 rgba(220, 50, 50, 0)
            );
        }
    """)

    return widget


# TODO: tamanho de fonte base específico (ex.: 10)

SMALLER_FONT = QFont()
SMALLER_FONT.setPointSize(8)

BIGGER_FONT = QFont()
BIGGER_FONT.setPointSize(14)
