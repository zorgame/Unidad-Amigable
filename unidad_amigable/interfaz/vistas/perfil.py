import flet as ft

from ...nucleo import ErrorAplicacion
from ...nucleo.entidades import Estudiante
from .. import tema
from ..componentes import campo, encabezado, formulario, mensaje_error, mostrar_error, subtitulo, tarjeta
from .base import Seccion


class Perfil(Seccion):
    def cargar(self) -> None:
        self.mostrar(
            encabezado("Mi perfil", "Mantén tus datos actualizados y protege el acceso a tu cuenta."),
            ft.ResponsiveRow(
                [
                    ft.Container(self._datos(), col={"xs": 12, "lg": 7}),
                    ft.Container(self._seguridad(), col={"xs": 12, "lg": 5}),
                ],
                spacing=16,
                run_spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    def _datos(self) -> ft.Container:
        usuario = self.usuario
        error = mensaje_error()
        campos = {
            "nombre": campo("Nombre completo", usuario.nombre, ft.Icons.PERSON_OUTLINE),
            "correo": campo("Correo electrónico", usuario.correo, ft.Icons.ALTERNATE_EMAIL),
        }
        filas: list[ft.Control] = [campos["nombre"], campos["correo"]]

        if isinstance(usuario, Estudiante):
            campos["programa_academico"] = campo("Programa académico", usuario.programa_academico,
                                                 ft.Icons.SCHOOL_OUTLINED)
            campos["semestre"] = campo("Semestre", str(usuario.semestre), expand=True,
                                       input_filter=ft.NumbersOnlyInputFilter())
            campos["edad"] = campo("Edad", str(usuario.edad), expand=True,
                                   input_filter=ft.NumbersOnlyInputFilter())
            filas += [
                campo("Código estudiantil", usuario.codigo, ft.Icons.BADGE_OUTLINED, read_only=True,
                      helper="El código no se puede modificar."),
                campos["programa_academico"],
                ft.Row([campos["semestre"], campos["edad"]], spacing=12),
            ]
        else:
            campos["cargo"] = campo("Cargo", usuario.cargo, ft.Icons.WORK_OUTLINE)
            filas.append(campos["cargo"])

        def guardar() -> None:
            try:
                actualizado = self.sistema.cuentas.actualizar_datos(
                    self.usuario, **{clave: control.value for clave, control in campos.items()}
                )
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            error.visible = False
            self.app.usuario = actualizado
            self.app.escritorio.refrescar_usuario()
            self.app.notificar("Tus datos se actualizaron correctamente.")

        return tarjeta(
            formulario(
                subtitulo("Datos personales"),
                *filas,
                error,
                ft.Row([ft.FilledButton(content="Guardar cambios", icon=ft.Icons.SAVE_OUTLINED, on_click=guardar)],
                       alignment=ft.MainAxisAlignment.END),
            ),
            padding=24,
        )

    def _seguridad(self) -> ft.Container:
        error = mensaje_error()
        actual = campo("Contraseña actual", password=True, can_reveal_password=True)
        nueva = campo("Nueva contraseña", password=True, can_reveal_password=True,
                      helper="Mínimo 8 caracteres, con letras y números.")
        confirmacion = campo("Confirmar nueva contraseña", password=True, can_reveal_password=True)

        def cambiar() -> None:
            try:
                self.sistema.cuentas.cambiar_contrasena(self.usuario, actual.value, nueva.value, confirmacion.value)
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            error.visible = False
            for control in (actual, nueva, confirmacion):
                control.value = ""
            self.app.notificar("Tu contraseña fue actualizada.")

        return tarjeta(
            formulario(
                subtitulo("Seguridad"),
                ft.Text("Usa una contraseña que no utilices en otros servicios.", size=13,
                        color=tema.TEXTO_SECUNDARIO),
                actual,
                nueva,
                confirmacion,
                error,
                ft.Row([ft.OutlinedButton(content="Cambiar contraseña", icon=ft.Icons.LOCK_RESET, on_click=cambiar)],
                       alignment=ft.MainAxisAlignment.END),
            ),
            padding=24,
        )
