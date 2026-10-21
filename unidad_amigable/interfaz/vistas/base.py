from typing import TYPE_CHECKING

import flet as ft

from ...nucleo.entidades import Usuario

if TYPE_CHECKING:
    from ..aplicacion import Aplicacion


class Seccion:
    def __init__(self, app: "Aplicacion") -> None:
        self.app = app
        self.sistema = app.sistema
        self.cuerpo = ft.Column(spacing=22, scroll=ft.ScrollMode.AUTO, expand=True)

    @property
    def usuario(self) -> Usuario:
        return self.app.usuario

    def construir(self) -> ft.Control:
        self.cargar()
        return self.cuerpo

    def mostrar(self, *controles: ft.Control) -> None:
        self.cuerpo.controls = list(controles)

    def cargar(self) -> None:
        raise NotImplementedError
