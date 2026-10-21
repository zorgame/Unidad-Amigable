from typing import TYPE_CHECKING, NamedTuple

import flet as ft

from .. import tema
from ..formato import iniciales
from .administracion import GestionCitas, GestionMetodos, GestionModulos, GestionUnidad, GestionUsuarios, Panel
from .base import Seccion
from .estudiante import Aprendizaje, Citas, Inicio, Metodos, Orientacion
from .perfil import Perfil

if TYPE_CHECKING:
    from ..aplicacion import Aplicacion


class Destino(NamedTuple):
    clave: str
    etiqueta: str
    icono: ft.IconData
    icono_activo: ft.IconData
    vista: type[Seccion]


DESTINOS_ESTUDIANTE = (
    Destino("inicio", "Inicio", ft.Icons.HOME_OUTLINED, ft.Icons.HOME_ROUNDED, Inicio),
    Destino("aprender", "Aprender", ft.Icons.MENU_BOOK_OUTLINED, ft.Icons.MENU_BOOK_ROUNDED, Aprendizaje),
    Destino("metodos", "Métodos", ft.Icons.HEALTH_AND_SAFETY_OUTLINED, ft.Icons.HEALTH_AND_SAFETY, Metodos),
    Destino("orientacion", "Orientación", ft.Icons.EXPLORE_OUTLINED, ft.Icons.EXPLORE, Orientacion),
    Destino("citas", "Mis citas", ft.Icons.EVENT_OUTLINED, ft.Icons.EVENT, Citas),
    Destino("perfil", "Mi perfil", ft.Icons.PERSON_OUTLINE, ft.Icons.PERSON, Perfil),
)

DESTINOS_ADMINISTRADOR = (
    Destino("panel", "Panel", ft.Icons.SPACE_DASHBOARD_OUTLINED, ft.Icons.SPACE_DASHBOARD, Panel),
    Destino("citas", "Citas", ft.Icons.EVENT_NOTE_OUTLINED, ft.Icons.EVENT_NOTE, GestionCitas),
    Destino("modulos", "Módulos", ft.Icons.LIBRARY_BOOKS_OUTLINED, ft.Icons.LIBRARY_BOOKS, GestionModulos),
    Destino("metodos", "Métodos", ft.Icons.MEDICATION_OUTLINED, ft.Icons.MEDICATION, GestionMetodos),
    Destino("usuarios", "Usuarios", ft.Icons.GROUP_OUTLINED, ft.Icons.GROUP, GestionUsuarios),
    Destino("unidad", "Unidad", ft.Icons.APARTMENT_OUTLINED, ft.Icons.APARTMENT, GestionUnidad),
    Destino("perfil", "Mi perfil", ft.Icons.PERSON_OUTLINE, ft.Icons.PERSON, Perfil),
)


class Escritorio:
    def __init__(self, app: "Aplicacion") -> None:
        self.app = app
        self.destinos = DESTINOS_ADMINISTRADOR if app.usuario.es_administrador else DESTINOS_ESTUDIANTE
        self.actual = self.destinos[0].clave
        self.menu = ft.Column(spacing=4)
        self.tarjeta_usuario = ft.Container()
        self.area = ft.Container(expand=True, padding=ft.Padding.symmetric(horizontal=36, vertical=28))

    def construir(self) -> ft.Control:
        self.refrescar_usuario()
        self.ir_a(self.actual)
        return ft.Row(
            [self._barra_lateral(), ft.VerticalDivider(width=1, color=tema.BORDE), self.area],
            expand=True,
            spacing=0,
        )

    def ir_a(self, clave: str) -> None:
        destino = next(d for d in self.destinos if d.clave == clave)
        self.actual = destino.clave
        self.menu.controls = [self._opcion(d) for d in self.destinos]
        self.area.content = destino.vista(self.app).construir()

    def refrescar_usuario(self) -> None:
        usuario = self.app.usuario
        self.tarjeta_usuario.content = ft.Row(
            [
                ft.CircleAvatar(
                    content=ft.Text(iniciales(usuario.nombre), weight=ft.FontWeight.W_600, size=13),
                    bgcolor=tema.PRIMARIO_SUAVE,
                    color=tema.PRIMARIO_OSCURO,
                    radius=19,
                ),
                ft.Column(
                    [
                        ft.Text(usuario.nombre, size=13, weight=ft.FontWeight.W_600, color=tema.TEXTO,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text("Administrador" if usuario.es_administrador else "Estudiante",
                                size=12, color=tema.TEXTO_SECUNDARIO),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color=tema.TEXTO_SECUNDARIO,
                    icon_size=20,
                    tooltip="Cerrar sesión",
                    on_click=self.app.mostrar_acceso,
                ),
            ],
            spacing=10,
        )

    def _opcion(self, destino: Destino) -> ft.Container:
        activo = destino.clave == self.actual
        color = tema.PRIMARIO_OSCURO if activo else tema.TEXTO_SECUNDARIO
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(destino.icono_activo if activo else destino.icono, color=color, size=22),
                    ft.Text(destino.etiqueta, size=14, color=color,
                            weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_500),
                ],
                spacing=14,
            ),
            padding=ft.Padding.symmetric(horizontal=14, vertical=11),
            border_radius=10,
            bgcolor=tema.PRIMARIO_SUAVE if activo else None,
            ink=True,
            on_click=lambda: self.ir_a(destino.clave),
        )

    def _barra_lateral(self) -> ft.Container:
        return ft.Container(
            width=248,
            bgcolor=tema.SUPERFICIE,
            padding=ft.Padding.symmetric(horizontal=16, vertical=22),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.FAVORITE_ROUNDED, color=ft.Colors.WHITE, size=20),
                                bgcolor=tema.PRIMARIO,
                                border_radius=10,
                                padding=8,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Unidad Amigable", size=16, weight=ft.FontWeight.W_700,
                                            color=tema.TEXTO),
                                    ft.Text("UCundinamarca · Girardot", size=11, color=tema.TEXTO_SECUNDARIO),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Container(height=18),
                    self.menu,
                    ft.Container(expand=True),
                    ft.Divider(height=1, color=tema.BORDE),
                    self.tarjeta_usuario,
                ],
                spacing=8,
            ),
        )
