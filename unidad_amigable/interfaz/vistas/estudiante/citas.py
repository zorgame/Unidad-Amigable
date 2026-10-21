from datetime import date

import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import MOTIVOS_CITA, Cita
from ... import tema
from ...componentes import (
    aviso,
    encabezado,
    formulario,
    insignia,
    mensaje_error,
    mostrar_error,
    selector,
    subtitulo,
    tarjeta,
    vacio,
)
from ...formato import MESES, fecha_larga, hora_legible
from ..base import Seccion


class SelectorFranja:
    def __init__(self, seccion: Seccion) -> None:
        self.citas = seccion.sistema.citas
        self.fecha = selector(
            "Fecha",
            [(d.isoformat(), fecha_larga(d)) for d in self.citas.fechas_disponibles()],
            icono=ft.Icons.CALENDAR_MONTH_OUTLINED,
            on_select=self._cargar_horas,
            menu_height=320,
            expand=True,
        )
        self.hora = selector("Hora", [], icono=ft.Icons.SCHEDULE, disabled=True, expand=True)

    def _cargar_horas(self) -> None:
        horas = self.citas.horas_disponibles(date.fromisoformat(self.fecha.value))
        self.hora.options = [ft.DropdownOption(key=h, text=hora_legible(h)) for h in horas]
        self.hora.value = None
        self.hora.disabled = not horas
        self.hora.hint_text = None if horas else "Sin horas libres"

    @property
    def dia(self) -> date | None:
        return date.fromisoformat(self.fecha.value) if self.fecha.value else None

    @property
    def controles(self) -> list[ft.Control]:
        return [ft.Row([self.fecha]), ft.Row([self.hora])]


class Citas(Seccion):
    def cargar(self) -> None:
        citas = self.sistema.citas.del_usuario(self.usuario)
        activa = next((c for c in citas if c.activa), None)
        self.mostrar(
            encabezado("Mis citas", "Agenda una asesoría privada con el personal de la Unidad Amigable."),
            ft.ResponsiveRow(
                [
                    ft.Container(self._formulario() if activa is None else self._activa(activa),
                                 col={"xs": 12, "lg": 5}),
                    ft.Container(self._listado(citas), col={"xs": 12, "lg": 7}),
                ],
                spacing=16,
                run_spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    def _formulario(self) -> ft.Container:
        franja = SelectorFranja(self)
        motivo = selector("Motivo de la consulta", [(m, m) for m in MOTIVOS_CITA],
                          icono=ft.Icons.CHAT_BUBBLE_OUTLINE, expand=True)
        error = mensaje_error()

        def agendar() -> None:
            try:
                self.sistema.citas.agendar(self.usuario, franja.dia, franja.hora.value, motivo.value)
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            self.cargar()
            self.app.notificar("Tu cita quedó agendada. Te esperamos.")

        return tarjeta(
            ft.Column(
                [
                    subtitulo("Agendar nueva cita"),
                    ft.Text("Atención de lunes a viernes en franjas de una hora.",
                            size=13, color=tema.TEXTO_SECUNDARIO),
                    *franja.controles,
                    ft.Row([motivo]),
                    error,
                    ft.Row(
                        [ft.FilledButton(content="Agendar cita", icon=ft.Icons.EVENT_AVAILABLE, on_click=agendar)],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=16,
            ),
            padding=24,
        )

    def _activa(self, cita: Cita) -> ft.Container:
        return tarjeta(
            ft.Column(
                [
                    subtitulo("Tienes una cita activa"),
                    ft.Text(f"{fecha_larga(cita.fecha)} · {hora_legible(cita.hora)}", size=18,
                            weight=ft.FontWeight.W_700, color=tema.PRIMARIO_OSCURO),
                    ft.Text(cita.motivo, size=14, color=tema.TEXTO_SECUNDARIO),
                    aviso("Para agendar una nueva cita, primero reprograma o cancela la actual."),
                    ft.Row(
                        [
                            ft.OutlinedButton(content="Cancelar", icon=ft.Icons.CLOSE,
                                              on_click=lambda: self._cancelar(cita)),
                            ft.FilledButton(content="Reprogramar", icon=ft.Icons.EDIT_CALENDAR,
                                            on_click=lambda: self._reprogramar(cita)),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                    ),
                ],
                spacing=14,
            ),
            padding=24,
            bgcolor=tema.PRIMARIO_SUAVE,
        )

    def _listado(self, citas: list[Cita]) -> ft.Container:
        if not citas:
            contenido: list[ft.Control] = [vacio(ft.Icons.EVENT_BUSY, "Todavía no has agendado citas.")]
        else:
            contenido = [self._fila(c) for c in citas]
        return tarjeta(ft.Column([subtitulo("Historial"), *contenido], spacing=12), padding=24)

    def _fila(self, cita: Cita) -> ft.Container:
        color, fondo = tema.COLORES_ESTADO[cita.estado]
        acciones: list[ft.Control] = []
        if cita.activa:
            acciones = [
                ft.IconButton(icon=ft.Icons.EDIT_CALENDAR, tooltip="Reprogramar", icon_color=tema.INFO,
                              on_click=lambda: self._reprogramar(cita)),
                ft.IconButton(icon=ft.Icons.EVENT_BUSY, tooltip="Cancelar", icon_color=tema.PELIGRO,
                              on_click=lambda: self._cancelar(cita)),
            ]
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(str(cita.fecha.day), size=20, weight=ft.FontWeight.W_700, color=color),
                                ft.Text(MESES[cita.fecha.month - 1][:3].upper(), size=11, color=color),
                            ],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=56,
                        padding=ft.Padding.symmetric(vertical=8),
                        bgcolor=fondo,
                        border_radius=10,
                    ),
                    ft.Column(
                        [
                            ft.Text(f"{fecha_larga(cita.fecha)} · {hora_legible(cita.hora)}", size=14,
                                    weight=ft.FontWeight.W_600, color=tema.TEXTO),
                            ft.Text(cita.motivo, size=13, color=tema.TEXTO_SECUNDARIO),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    insignia(cita.estado, color, fondo),
                    *acciones,
                ],
                spacing=14,
            ),
            padding=10,
            border=ft.Border.all(1, tema.BORDE),
            border_radius=12,
        )

    def _cancelar(self, cita: Cita) -> None:
        def ejecutar() -> None:
            try:
                self.sistema.citas.cancelar(self.usuario, cita.id_cita)
            except ErrorAplicacion as fallo:
                self.app.notificar(str(fallo), error=True)
                return
            self.cargar()
            self.app.notificar("La cita fue cancelada.")

        self.app.confirmar(
            "Cancelar cita",
            f"¿Seguro que quieres cancelar tu cita del {fecha_larga(cita.fecha).lower()} "
            f"a las {hora_legible(cita.hora)}?",
            ejecutar,
            "Cancelar cita",
        )

    def _reprogramar(self, cita: Cita) -> None:
        franja = SelectorFranja(self)
        error = mensaje_error()

        def guardar() -> None:
            try:
                self.sistema.citas.reprogramar(self.usuario, cita.id_cita, franja.dia, franja.hora.value)
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            self.app.cerrar_dialogo()
            self.cargar()
            self.app.notificar("Tu cita fue reprogramada.")

        self.app.abrir_dialogo(
            "Reprogramar cita",
            formulario(
                ft.Text(f"Actual: {fecha_larga(cita.fecha)} · {hora_legible(cita.hora)}",
                        size=13, color=tema.TEXTO_SECUNDARIO),
                *franja.controles,
                error,
            ),
            [
                ft.TextButton(content="Volver", on_click=self.app.cerrar_dialogo),
                ft.FilledButton(content="Guardar cambios", on_click=guardar),
            ],
            ancho=420,
        )
