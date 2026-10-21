import flet as ft

from ....nucleo import ErrorAplicacion
from ... import tema
from ...componentes import aviso, campo, encabezado, formulario, mensaje_error, mostrar_error, subtitulo, tarjeta
from ..base import Seccion


class GestionUnidad(Seccion):
    def cargar(self) -> None:
        unidad = self.sistema.contenido.unidad()
        nombre = campo("Nombre de la unidad", unidad.nombre, ft.Icons.APARTMENT_OUTLINED)
        ubicacion = campo("Ubicación", unidad.ubicacion, ft.Icons.PLACE_OUTLINED)
        contacto = campo("Contacto", unidad.contacto, ft.Icons.CONTACT_MAIL_OUTLINED)
        error = mensaje_error()

        def guardar() -> None:
            try:
                self.sistema.contenido.actualizar_unidad(self.usuario, nombre.value, ubicacion.value, contacto.value)
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            error.visible = False
            self.app.notificar("La información de la unidad fue actualizada.")

        self.mostrar(
            encabezado("Unidad Amigable", "Datos de contacto que ven los estudiantes en su inicio."),
            ft.ResponsiveRow(
                [
                    tarjeta(
                        formulario(
                            subtitulo("Información general"),
                            nombre,
                            ubicacion,
                            contacto,
                            error,
                            ft.Row([ft.FilledButton(content="Guardar cambios", icon=ft.Icons.SAVE_OUTLINED,
                                                    on_click=guardar)],
                                   alignment=ft.MainAxisAlignment.END),
                        ),
                        padding=24,
                        col={"xs": 12, "lg": 7},
                    ),
                    ft.Container(
                        aviso("Todas las citas agendadas se asignan a esta unidad. Los horarios de atención "
                              "son de lunes a viernes, de 8:00 a. m. a 12:00 m. y de 2:00 p. m. a 5:00 p. m.",
                              ft.Icons.INFO_OUTLINE, tema.INFO, tema.INFO_SUAVE),
                        col={"xs": 12, "lg": 5},
                    ),
                ],
                spacing=16,
                run_spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )
