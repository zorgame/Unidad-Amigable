import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import Cita, EstadoCita
from ... import tema
from ...componentes import celda, celda_doble, encabezado, insignia, tabla, tarjeta, vacio
from ...formato import fecha_corta, hora_legible
from ..base import Seccion

TODAS = "todas"


class GestionCitas(Seccion):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.filtro = TODAS
        self.contenedor = ft.Container()

    def cargar(self) -> None:
        self._listar()
        self.mostrar(
            encabezado("Citas", "Confirma, atiende o cancela las solicitudes de los estudiantes."),
            ft.SegmentedButton(
                segments=[ft.Segment(value=TODAS, label="Todas"),
                          *[ft.Segment(value=e.value, label=e.value) for e in EstadoCita]],
                selected=[self.filtro],
                show_selected_icon=False,
                on_change=self._filtrar,
            ),
            self.contenedor,
        )

    def _filtrar(self, e: ft.Event[ft.SegmentedButton]) -> None:
        self.filtro = e.control.selected[0]
        self._listar()

    def _listar(self) -> None:
        estado = None if self.filtro == TODAS else EstadoCita(self.filtro)
        citas = self.sistema.citas.listar(self.usuario, estado)
        if not citas:
            self.contenedor.content = tarjeta(vacio(ft.Icons.EVENT_BUSY, "No hay citas con este estado."))
            return
        self.contenedor.content = tarjeta(
            tabla(
                ["Fecha", "Hora", "Estudiante", "Motivo", "Estado", "Acciones"],
                [
                    [
                        celda(fecha_corta(c.fecha), negrita=True),
                        celda(hora_legible(c.hora)),
                        celda_doble(c.estudiante, f"Código {c.codigo}", 190),
                        celda(c.motivo, ancho=200),
                        insignia(c.estado, *tema.COLORES_ESTADO[c.estado]),
                        self._acciones(c),
                    ]
                    for c in citas
                ],
            ),
            padding=8,
        )

    def _acciones(self, cita: Cita) -> ft.Row:
        if not cita.activa:
            return ft.Row([ft.Text("—", color=tema.TEXTO_SECUNDARIO)])
        botones = []
        if cita.estado is EstadoCita.PENDIENTE:
            botones.append(ft.IconButton(icon=ft.Icons.THUMB_UP_ALT_OUTLINED, tooltip="Confirmar",
                                         icon_color=tema.INFO,
                                         on_click=lambda: self._cambiar(cita, EstadoCita.CONFIRMADA)))
        botones += [
            ft.IconButton(icon=ft.Icons.TASK_ALT, tooltip="Marcar como atendida", icon_color=tema.PRIMARIO,
                          on_click=lambda: self._cambiar(cita, EstadoCita.ATENDIDA)),
            ft.IconButton(icon=ft.Icons.EVENT_BUSY, tooltip="Cancelar", icon_color=tema.PELIGRO,
                          on_click=lambda: self.app.confirmar(
                              "Cancelar cita",
                              f"Se cancelará la cita de {cita.estudiante}. El horario quedará libre.",
                              lambda: self._cambiar(cita, EstadoCita.CANCELADA),
                              "Cancelar cita",
                          )),
        ]
        return ft.Row(botones, spacing=0)

    def _cambiar(self, cita: Cita, estado: EstadoCita) -> None:
        try:
            self.sistema.citas.cambiar_estado(self.usuario, cita.id_cita, estado)
        except ErrorAplicacion as fallo:
            self.app.notificar(str(fallo), error=True)
            return
        self._listar()
        self.app.notificar(f"Cita de {cita.estudiante} marcada como {estado.lower()}.")
