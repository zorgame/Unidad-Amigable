import flet as ft

from ... import tema
from ...componentes import barra, encabezado, indicador, insignia, subtitulo, tarjeta, vacio
from ...formato import fecha_larga, hora_legible
from ..base import Seccion

class Panel(Seccion):
    def cargar(self) -> None:
        resumen = self.sistema.reportes.resumen(self.usuario)
        columnas = {"xs": 12, "sm": 6, "xl": 3}
        self.mostrar(
            encabezado(
                "Panel de la Unidad",
                "Indicadores de uso del prototipo y actividad de los estudiantes.",
                [ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Actualizar", on_click=self.cargar)],
            ),
            ft.ResponsiveRow(
                [
                    indicador(ft.Icons.GROUP_OUTLINED, str(resumen.estudiantes), "Estudiantes registrados",
                              col=columnas),
                    indicador(ft.Icons.PENDING_ACTIONS, str(resumen.citas_pendientes), "Citas por atender",
                              tema.AVISO, tema.AVISO_SUAVE, col=columnas),
                    indicador(ft.Icons.TASK_ALT, str(resumen.citas_atendidas), "Citas atendidas",
                              tema.INFO, tema.INFO_SUAVE, col=columnas),
                    indicador(ft.Icons.QUIZ_OUTLINED, str(resumen.evaluaciones), "Evaluaciones presentadas",
                              tema.MORADO, tema.MORADO_SUAVE, col=columnas),
                ],
                spacing=16,
                run_spacing=16,
            ),
            ft.ResponsiveRow(
                [
                    tarjeta(self._metodos(resumen.metodos_recomendados, resumen.orientaciones),
                            col={"xs": 12, "lg": 6}, padding=24),
                    tarjeta(self._modulos(resumen.rendimiento_modulos), col={"xs": 12, "lg": 6}, padding=24),
                ],
                spacing=16,
                run_spacing=16,
            ),
            tarjeta(self._agenda(), padding=24),
        )

    @staticmethod
    def _metodos(conteo: list[tuple[str, int]], total: int) -> ft.Column:
        cabecera = [subtitulo("Métodos más sugeridos"),
                    ft.Text(f"Basado en {total} orientaciones realizadas.", size=13, color=tema.TEXTO_SECUNDARIO)]
        if not conteo:
            return ft.Column([*cabecera, vacio(ft.Icons.INSIGHTS, "Aún no hay orientaciones registradas.")])
        mayor = conteo[0][1]
        return ft.Column(
            [*cabecera, *[barra(nombre, str(veces), veces / mayor) for nombre, veces in conteo]],
            spacing=14,
        )

    @staticmethod
    def _modulos(rendimiento: list[tuple[str, int, int]]) -> ft.Column:
        cabecera = [subtitulo("Rendimiento por módulo"),
                    ft.Text("Promedio de aciertos en las evaluaciones.", size=13, color=tema.TEXTO_SECUNDARIO)]
        if not rendimiento:
            return ft.Column([*cabecera, vacio(ft.Icons.QUERY_STATS, "Aún no hay evaluaciones presentadas.")])
        return ft.Column(
            [
                *cabecera,
                *[
                    barra(titulo, f"{promedio} % · {intentos} intento(s)", promedio / 100,
                          tema.PRIMARIO if promedio >= 70 else tema.AVISO)
                    for titulo, promedio, intentos in rendimiento
                ],
            ],
            spacing=14,
        )

    def _agenda(self) -> ft.Column:
        proximas = [c for c in self.sistema.citas.listar(self.usuario) if c.activa][:5]
        filas: list[ft.Control] = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.EVENT, color=tema.PRIMARIO, size=20),
                    ft.Text(f"{fecha_larga(c.fecha)} · {hora_legible(c.hora)}", size=14,
                            weight=ft.FontWeight.W_600, color=tema.TEXTO, width=260),
                    ft.Text(c.estudiante, size=14, color=tema.TEXTO, expand=True),
                    ft.Text(c.motivo, size=13, color=tema.TEXTO_SECUNDARIO, expand=True),
                    insignia(c.estado, *tema.COLORES_ESTADO[c.estado]),
                ],
                spacing=14,
            )
            for c in proximas
        ]
        return ft.Column(
            [
                ft.Row(
                    [subtitulo("Próximas citas"), ft.Container(expand=True),
                     ft.TextButton(content="Ver todas", on_click=lambda: self.app.ir_a("citas"))]
                ),
                *(filas or [vacio(ft.Icons.EVENT_AVAILABLE, "No hay citas pendientes.")]),
            ],
            spacing=12,
        )
