from collections.abc import Callable

import flet as ft

from ..nucleo import Sistema
from ..nucleo.entidades import Usuario
from . import tema
from .vistas.acceso import PantallaAcceso
from .vistas.escritorio import Escritorio


class Aplicacion:
    def __init__(self, page: ft.Page, sistema: Sistema) -> None:
        self.page = page
        self.sistema = sistema
        self.usuario: Usuario | None = None
        self.escritorio: Escritorio | None = None

    def iniciar(self) -> None:
        tema.aplicar(self.page)
        self.mostrar_acceso()

    def _montar(self, control: ft.Control) -> None:
        self.page.controls.clear()
        self.page.add(control)

    def mostrar_acceso(self) -> None:
        self.usuario = None
        self.escritorio = None
        self._montar(PantallaAcceso(self).construir())

    def entrar(self, usuario: Usuario) -> None:
        self.usuario = usuario
        self.escritorio = Escritorio(self)
        self._montar(self.escritorio.construir())

    def ir_a(self, clave: str) -> None:
        if self.escritorio:
            self.escritorio.ir_a(clave)

    def notificar(self, mensaje: str, error: bool = False) -> None:
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINE if error else ft.Icons.CHECK_CIRCLE_OUTLINE,
                                color=ft.Colors.WHITE, size=20),
                        ft.Text(mensaje, color=ft.Colors.WHITE, expand=True),
                    ],
                    spacing=10,
                ),
                bgcolor=tema.PELIGRO if error else tema.PRIMARIO_OSCURO,
                behavior=ft.SnackBarBehavior.FLOATING,
                width=460,
                duration=ft.Duration(seconds=4),
            )
        )
        self.page.update()

    def abrir_dialogo(self, titulo: str, contenido: ft.Control, acciones: list[ft.Control],
                      ancho: int = 480) -> ft.AlertDialog:
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, size=20, weight=ft.FontWeight.W_700),
            content=ft.Container(content=contenido, width=ancho),
            actions=acciones,
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=tema.RADIO),
            bgcolor=tema.SUPERFICIE,
            scrollable=True,
        )
        self.page.show_dialog(dialogo)
        return dialogo

    def cerrar_dialogo(self) -> None:
        self.page.pop_dialog()

    def confirmar(self, titulo: str, mensaje: str, accion: Callable[[], None],
                  texto_accion: str = "Confirmar") -> None:
        def aceptar() -> None:
            self.cerrar_dialogo()
            accion()
            self.page.update()

        self.abrir_dialogo(
            titulo,
            ft.Text(mensaje, size=14, color=tema.TEXTO_SECUNDARIO),
            [
                ft.TextButton(content="Volver", on_click=self.cerrar_dialogo),
                ft.FilledButton(content=texto_accion, on_click=aceptar,
                                style=ft.ButtonStyle(bgcolor=tema.PELIGRO)),
            ],
            ancho=400,
        )
