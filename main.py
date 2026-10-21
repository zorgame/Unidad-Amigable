from pathlib import Path

import flet as ft

from unidad_amigable.interfaz import Aplicacion
from unidad_amigable.nucleo import Sistema

RUTA_BASE_DATOS = Path(__file__).resolve().parent / "datos" / "unidad_amigable.db"


def main(page: ft.Page) -> None:
    Aplicacion(page, Sistema(RUTA_BASE_DATOS)).iniciar()


if __name__ == "__main__":
    ft.run(main)
