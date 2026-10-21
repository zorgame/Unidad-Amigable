from typing import TYPE_CHECKING

import flet as ft

from ...nucleo import ErrorAplicacion
from .. import tema
from ..componentes import campo, mensaje_error, mostrar_error

if TYPE_CHECKING:
    from ..aplicacion import Aplicacion


class PantallaAcceso:
    def __init__(self, app: "Aplicacion") -> None:
        self.app = app
        self.formulario = ft.Container(width=420)
        self.error = mensaje_error()

    def construir(self) -> ft.Control:
        self._formulario_ingreso()
        return ft.Row(
            [
                self._presentacion(),
                ft.Container(
                    content=ft.Column(
                        [self.formulario],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=6,
                    alignment=ft.Alignment.CENTER,
                    padding=32,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _presentacion(self) -> ft.Container:
        puntos = [
            (ft.Icons.MENU_BOOK_OUTLINED, "Módulos educativos con evaluación"),
            (ft.Icons.HEALTH_AND_SAFETY_OUTLINED, "Información confiable sobre métodos"),
            (ft.Icons.EXPLORE_OUTLINED, "Orientación personalizada y seguimiento"),
            (ft.Icons.EVENT_AVAILABLE_OUTLINED, "Citas con la Unidad Amigable"),
        ]
        return ft.Container(
            expand=5,
            padding=56,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[tema.PRIMARIO_OSCURO, tema.PRIMARIO, tema.ACENTO],
            ),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.FAVORITE_ROUNDED, color=tema.PRIMARIO, size=30),
                                bgcolor=ft.Colors.WHITE,
                                border_radius=16,
                                padding=12,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Unidad Amigable", size=24, weight=ft.FontWeight.W_700,
                                            color=ft.Colors.WHITE),
                                    ft.Text("Universidad de Cundinamarca · Girardot", size=13,
                                            color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=14,
                    ),
                    ft.Container(expand=True),
                    ft.Text("Cuidarte es quererte", size=38, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                    ft.Text(
                        "Información, orientación y acompañamiento en salud sexual y reproductiva, "
                        "en un espacio privado y sin juicios.",
                        size=15,
                        color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                    ),
                    ft.Container(height=12),
                    *[
                        ft.Row(
                            [ft.Icon(icono, color=ft.Colors.WHITE, size=20),
                             ft.Text(texto, color=ft.Colors.WHITE, size=14)],
                            spacing=12,
                        )
                        for icono, texto in puntos
                    ],
                    ft.Container(expand=True),
                    ft.Text("Tu información es confidencial.", size=12,
                            color=ft.Colors.with_opacity(0.75, ft.Colors.WHITE)),
                ],
                spacing=14,
            ),
        )

    def _cabecera(self, titulo: str, descripcion: str) -> list[ft.Control]:
        return [
            ft.Text(titulo, size=28, weight=ft.FontWeight.W_700, color=tema.TEXTO),
            ft.Text(descripcion, size=14, color=tema.TEXTO_SECUNDARIO),
            ft.Container(height=8),
        ]

    def _cambiar(self, texto: str, enlace: str, destino) -> ft.Row:
        return ft.Row(
            [
                ft.Text(texto, size=13, color=tema.TEXTO_SECUNDARIO),
                ft.TextButton(content=enlace, on_click=destino),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        )

    def _formulario_ingreso(self) -> None:
        self.error.visible = False
        correo = campo("Correo institucional", icono=ft.Icons.ALTERNATE_EMAIL, autofocus=True)
        contrasena = campo("Contraseña", icono=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True)

        def ingresar() -> None:
            try:
                usuario = self.app.sistema.cuentas.iniciar_sesion(correo.value, contrasena.value)
            except ErrorAplicacion as error:
                mostrar_error(self.error, str(error))
                return
            self.app.entrar(usuario)

        async def siguiente() -> None:
            await contrasena.focus()

        correo.on_submit = siguiente
        contrasena.on_submit = ingresar

        self.formulario.content = ft.Column(
            [
                *self._cabecera("Iniciar sesión", "Ingresa con tu cuenta para continuar."),
                correo,
                contrasena,
                self.error,
                ft.FilledButton(content="Ingresar", icon=ft.Icons.LOGIN, on_click=ingresar, height=48),
                self._cambiar("¿Aún no tienes cuenta?", "Regístrate", self._formulario_registro),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def _formulario_registro(self) -> None:
        self.error.visible = False
        nombre = campo("Nombre completo", icono=ft.Icons.PERSON_OUTLINE, autofocus=True)
        correo = campo("Correo electrónico", icono=ft.Icons.ALTERNATE_EMAIL)
        codigo = campo("Código estudiantil", icono=ft.Icons.BADGE_OUTLINED, input_filter=ft.NumbersOnlyInputFilter())
        programa = campo("Programa académico", icono=ft.Icons.SCHOOL_OUTLINED)
        semestre = campo("Semestre", input_filter=ft.NumbersOnlyInputFilter(), expand=True)
        edad = campo("Edad", input_filter=ft.NumbersOnlyInputFilter(), expand=True)
        contrasena = campo("Contraseña", icono=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True,
                           helper="Mínimo 8 caracteres, con letras y números.")

        def registrar() -> None:
            try:
                usuario = self.app.sistema.cuentas.registrar_estudiante(
                    nombre.value, correo.value, contrasena.value, codigo.value,
                    programa.value, semestre.value, edad.value,
                )
            except ErrorAplicacion as error:
                mostrar_error(self.error, str(error))
                return
            self.app.entrar(usuario)
            self.app.notificar(f"Cuenta creada. Te damos la bienvenida, {usuario.nombre.split()[0]}.")

        self.formulario.content = ft.Column(
            [
                *self._cabecera("Crear cuenta", "Regístrate como estudiante de la Universidad."),
                nombre,
                correo,
                codigo,
                programa,
                ft.Row([semestre, edad], spacing=12),
                contrasena,
                self.error,
                ft.FilledButton(content="Crear cuenta", icon=ft.Icons.PERSON_ADD_ALT, on_click=registrar,
                                height=48),
                self._cambiar("¿Ya tienes cuenta?", "Inicia sesión", self._formulario_ingreso),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
