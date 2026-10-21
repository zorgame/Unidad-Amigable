import flet as ft

from ... import tema
from ...componentes import barra, encabezado, icono_circular, indicador, subtitulo, tarjeta
from ...formato import fecha_corta, hora_legible, primer_nombre
from ..base import Seccion

ACCESOS = (
    ("aprender", ft.Icons.MENU_BOOK_ROUNDED, "Aprender", "Módulos cortos sobre anticoncepción, ITS y derechos."),
    ("metodos", ft.Icons.HEALTH_AND_SAFETY, "Conocer métodos", "Compara efectividad, duración y cuidados."),
    ("orientacion", ft.Icons.EXPLORE, "Recibir orientación", "Responde 5 preguntas y descubre opciones para ti."),
    ("citas", ft.Icons.EVENT, "Agendar cita", "Habla en privado con el personal de la Unidad."),
)


class Inicio(Seccion):
    def cargar(self) -> None:
        modulos = self.sistema.contenido.listar_modulos()
        progreso = self.sistema.evaluaciones.progreso(self.usuario)
        aprobados = sum(e.aprobada for e in progreso.values())
        proxima = self.sistema.citas.proxima(self.usuario)
        orientaciones = self.sistema.orientacion.historial(self.usuario)
        columnas = {"xs": 12, "md": 4}

        self.mostrar(
            encabezado(
                f"Hola, {primer_nombre(self.usuario.nombre)}",
                "Este es tu espacio para aprender, resolver dudas y cuidar tu salud sexual.",
            ),
            ft.ResponsiveRow(
                [
                    indicador(ft.Icons.WORKSPACE_PREMIUM_OUTLINED, f"{aprobados} de {len(modulos)}",
                              "Módulos aprobados", col=columnas),
                    indicador(
                        ft.Icons.EVENT_AVAILABLE_OUTLINED,
                        f"{fecha_corta(proxima.fecha)} · {hora_legible(proxima.hora)}" if proxima else "Sin agendar",
                        "Próxima cita",
                        tema.INFO,
                        tema.INFO_SUAVE,
                        col=columnas,
                    ),
                    indicador(ft.Icons.INSIGHTS_OUTLINED, str(len(orientaciones)), "Orientaciones realizadas",
                              tema.MORADO, tema.MORADO_SUAVE, col=columnas),
                ],
                spacing=16,
                run_spacing=16,
            ),
            subtitulo("¿Qué quieres hacer hoy?"),
            ft.ResponsiveRow([self._acceso(*a) for a in ACCESOS], spacing=16, run_spacing=16),
            ft.ResponsiveRow(
                [
                    tarjeta(self._progreso(modulos, progreso), col={"xs": 12, "lg": 7}),
                    tarjeta(self._unidad(), col={"xs": 12, "lg": 5}),
                ],
                spacing=16,
                run_spacing=16,
            ),
        )

    def _acceso(self, clave: str, icono: ft.IconData, titulo: str, descripcion: str) -> ft.Container:
        return tarjeta(
            ft.Column(
                [
                    icono_circular(icono),
                    ft.Text(titulo, size=15, weight=ft.FontWeight.W_600, color=tema.TEXTO),
                    ft.Text(descripcion, size=13, color=tema.TEXTO_SECUNDARIO),
                ],
                spacing=10,
            ),
            col={"xs": 12, "sm": 6, "xl": 3},
            on_click=lambda: self.app.ir_a(clave),
        )

    def _progreso(self, modulos, progreso) -> ft.Column:
        filas: list[ft.Control] = [subtitulo("Tu progreso de aprendizaje")]
        for modulo in modulos:
            evaluacion = progreso.get(modulo.id_modulo)
            porcentaje = evaluacion.porcentaje if evaluacion else 0
            filas.append(
                barra(
                    modulo.titulo,
                    f"{porcentaje} %" if evaluacion else "Pendiente",
                    porcentaje / 100,
                    tema.PRIMARIO if evaluacion and evaluacion.aprobada else tema.AVISO,
                )
            )
        return ft.Column(filas, spacing=14)

    def _unidad(self) -> ft.Column:
        unidad = self.sistema.contenido.unidad()
        detalle = (
            (ft.Icons.APARTMENT_OUTLINED, unidad.nombre),
            (ft.Icons.PLACE_OUTLINED, unidad.ubicacion),
            (ft.Icons.MAIL_OUTLINE, unidad.contacto),
            (ft.Icons.SCHEDULE_OUTLINED, "Lunes a viernes · 8:00 a. m. a 5:00 p. m."),
        )
        return ft.Column(
            [
                subtitulo("Tu Unidad Amigable"),
                *[
                    ft.Row(
                        [ft.Icon(icono, size=18, color=tema.PRIMARIO),
                         ft.Text(texto, size=13, color=tema.TEXTO, expand=True, selectable=True)],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                    for icono, texto in detalle
                ],
                ft.Container(height=4),
                ft.FilledButton(content="Agendar asesoría", icon=ft.Icons.EVENT, on_click=lambda: self.app.ir_a("citas")),
            ],
            spacing=14,
        )
