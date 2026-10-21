import flet as ft

from ..nucleo.entidades import EstadoCita

PRIMARIO = "#2E7D32"
PRIMARIO_OSCURO = "#1B5E20"
PRIMARIO_SUAVE = "#E8F5E9"
ACENTO = "#7CB342"
FONDO = "#F4F7F4"
SUPERFICIE = "#FFFFFF"
BORDE = "#E0E7E1"
TEXTO = "#1D2B20"
TEXTO_SECUNDARIO = "#5D6B61"
PELIGRO = "#C62828"
PELIGRO_SUAVE = "#FDECEA"
AVISO = "#B26A00"
AVISO_SUAVE = "#FFF4E0"
INFO = "#1565C0"
INFO_SUAVE = "#E3F0FD"
MORADO = "#6A1B9A"
MORADO_SUAVE = "#F3E5F5"

RADIO = 14

COLORES_ESTADO = {
    EstadoCita.PENDIENTE: (AVISO, AVISO_SUAVE),
    EstadoCita.CONFIRMADA: (INFO, INFO_SUAVE),
    EstadoCita.ATENDIDA: (PRIMARIO, PRIMARIO_SUAVE),
    EstadoCita.CANCELADA: (PELIGRO, PELIGRO_SUAVE),
}

COLORES_TIPO = {
    "Hormonal": (MORADO, MORADO_SUAVE),
    "Intrauterino": (INFO, INFO_SUAVE),
    "Barrera": (PRIMARIO, PRIMARIO_SUAVE),
    "Emergencia": (PELIGRO, PELIGRO_SUAVE),
}

def aplicar(page: ft.Page) -> None:
    page.title = "Unidad Amigable"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=PRIMARIO, font_family="Segoe UI")
    page.bgcolor = FONDO
    page.padding = 0
    page.spacing = 0
    page.window.width = 1280
    page.window.height = 820
    page.window.min_width = 1000
    page.window.min_height = 660