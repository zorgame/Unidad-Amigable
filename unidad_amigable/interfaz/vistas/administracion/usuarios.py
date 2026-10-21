from datetime import datetime

import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import Estudiante, Usuario
from ... import tema
from ...componentes import (
    campo,
    celda,
    celda_doble,
    encabezado,
    formulario,
    insignia,
    mensaje_error,
    mostrar_error,
    tabla,
    tarjeta,
    vacio,
)
from ...formato import fecha_corta
from ..base import Seccion


class GestionUsuarios(Seccion):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.contenedor = ft.Container()
        self.busqueda = campo("Buscar por nombre, correo o código", icono=ft.Icons.SEARCH,
                              on_change=self._listar, width=360)

    def cargar(self) -> None:
        self._listar()
        self.mostrar(
            encabezado(
                "Usuarios",
                "Consulta las cuentas registradas y gestiona el acceso administrativo.",
                [ft.FilledButton(content="Nuevo administrador", icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                                 on_click=self._nuevo_administrador)],
            ),
            self.busqueda,
            self.contenedor,
        )

    def _coincide(self, usuario: Usuario) -> bool:
        termino = (self.busqueda.value or "").strip().lower()
        codigo = usuario.codigo if isinstance(usuario, Estudiante) else ""
        return not termino or any(termino in v.lower() for v in (usuario.nombre, usuario.correo, codigo))

    def _listar(self) -> None:
        registros = [(u, f) for u, f in self.sistema.cuentas.listar(self.usuario) if self._coincide(u)]
        if not registros:
            self.contenedor.content = tarjeta(vacio(ft.Icons.PERSON_SEARCH, "No hay usuarios que coincidan."))
            return
        self.contenedor.content = tarjeta(
            tabla(
                ["Usuario", "Rol", "Código", "Programa o cargo", "Semestre", "Registro", ""],
                [self._fila(u, f) for u, f in registros],
            ),
            padding=8,
        )

    def _fila(self, usuario: Usuario, registro: datetime) -> list[ft.Control]:
        estudiante = isinstance(usuario, Estudiante)
        propio = usuario.id_usuario == self.usuario.id_usuario
        return [
            celda_doble(usuario.nombre, usuario.correo, 220),
            insignia("Estudiante", tema.PRIMARIO, tema.PRIMARIO_SUAVE) if estudiante
            else insignia("Administrador", tema.MORADO, tema.MORADO_SUAVE),
            celda(usuario.codigo if estudiante else "—"),
            celda(usuario.programa_academico if estudiante else usuario.cargo, ancho=170),
            celda(str(usuario.semestre) if estudiante else "—"),
            celda(fecha_corta(registro)),
            ft.Container(width=40) if propio else ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=tema.PELIGRO,
                tooltip="Eliminar cuenta",
                on_click=lambda: self._eliminar(usuario),
            ),
        ]

    def _eliminar(self, usuario: Usuario) -> None:
        def ejecutar() -> None:
            try:
                self.sistema.cuentas.eliminar(self.usuario, usuario.id_usuario)
            except ErrorAplicacion as fallo:
                self.app.notificar(str(fallo), error=True)
                return
            self._listar()
            self.app.notificar(f"La cuenta de {usuario.nombre} fue eliminada.")

        self.app.confirmar(
            "Eliminar cuenta",
            f"Se eliminará la cuenta de {usuario.nombre} con sus citas, evaluaciones y orientaciones. "
            "Esta acción no se puede deshacer.",
            ejecutar,
            "Eliminar",
        )

    def _nuevo_administrador(self) -> None:
        nombre = campo("Nombre completo", icono=ft.Icons.PERSON_OUTLINE)
        correo = campo("Correo electrónico", icono=ft.Icons.ALTERNATE_EMAIL)
        cargo = campo("Cargo", icono=ft.Icons.WORK_OUTLINE)
        contrasena = campo("Contraseña temporal", icono=ft.Icons.LOCK_OUTLINE, password=True,
                           can_reveal_password=True, helper="Mínimo 8 caracteres, con letras y números.")
        error = mensaje_error()

        def crear() -> None:
            try:
                nuevo = self.sistema.cuentas.registrar_administrador(
                    self.usuario, nombre.value, correo.value, contrasena.value, cargo.value
                )
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            self.app.cerrar_dialogo()
            self._listar()
            self.app.notificar(f"Se creó la cuenta administrativa de {nuevo.nombre}.")

        self.app.abrir_dialogo(
            "Nuevo administrador",
            formulario(nombre, correo, cargo, contrasena, error),
            [
                ft.TextButton(content="Cancelar", on_click=self.app.cerrar_dialogo),
                ft.FilledButton(content="Crear cuenta", icon=ft.Icons.PERSON_ADD_ALT, on_click=crear),
            ],
        )