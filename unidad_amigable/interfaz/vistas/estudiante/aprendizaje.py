import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import Evaluacion, ModuloEducativo, Pregunta
from ... import tema
from ...componentes import aviso, encabezado, icono_circular, insignia, subtitulo, tarjeta
from ..base import Seccion

ICONOS_CONTENIDO = {
    "Lectura": ft.Icons.ARTICLE_OUTLINED,
    "Guía práctica": ft.Icons.CHECKLIST_ROUNDED,
    "Preguntas frecuentes": ft.Icons.QUESTION_ANSWER_OUTLINED,
}


class Aprendizaje(Seccion):
    def cargar(self) -> None:
        progreso = self.sistema.evaluaciones.progreso(self.usuario)
        self.mostrar(
            encabezado("Módulos educativos", "Lee cada módulo a tu ritmo y comprueba lo aprendido con su evaluación."),
            ft.ResponsiveRow(
                [self._tarjeta_modulo(m, progreso.get(m.id_modulo)) for m in self.sistema.contenido.listar_modulos()],
                spacing=16,
                run_spacing=16,
            ),
        )

    def _estado(self, evaluacion: Evaluacion | None) -> ft.Control:
        if evaluacion is None:
            return insignia("Sin evaluar", tema.TEXTO_SECUNDARIO, tema.FONDO)
        if evaluacion.aprobada:
            return insignia(f"Aprobado · {evaluacion.porcentaje} %", tema.PRIMARIO, tema.PRIMARIO_SUAVE,
                            ft.Icons.CHECK_CIRCLE)
        return insignia(f"Por mejorar · {evaluacion.porcentaje} %", tema.AVISO, tema.AVISO_SUAVE)

    def _tarjeta_modulo(self, modulo: ModuloEducativo, evaluacion: Evaluacion | None) -> ft.Container:
        return tarjeta(
            ft.Column(
                [
                    ft.Row(
                        [
                            icono_circular(ICONOS_CONTENIDO.get(modulo.tipo_contenido, ft.Icons.ARTICLE_OUTLINED)),
                            ft.Container(expand=True),
                            self._estado(evaluacion),
                        ]
                    ),
                    ft.Text(modulo.tema.upper(), size=11, weight=ft.FontWeight.W_600, color=tema.ACENTO),
                    ft.Text(modulo.titulo, size=16, weight=ft.FontWeight.W_600, color=tema.TEXTO,
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(modulo.tipo_contenido, size=13, color=tema.TEXTO_SECUNDARIO),
                    ft.Row(
                        [ft.TextButton(content="Abrir módulo", icon=ft.Icons.ARROW_FORWARD,
                                       on_click=lambda: self.abrir(modulo))],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=8,
            ),
            col={"xs": 12, "md": 6, "xl": 4},
            on_click=lambda: self.abrir(modulo),
        )

    def _volver(self, titulo: str, destino) -> ft.Row:
        return ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Volver", on_click=destino),
                ft.Text(titulo, size=22, weight=ft.FontWeight.W_700, color=tema.TEXTO, expand=True),
            ],
            spacing=8,
        )

    def abrir(self, modulo: ModuloEducativo) -> None:
        evaluable = modulo.id_modulo in self.sistema.contenido.modulos_evaluables()
        acciones: list[ft.Control] = [ft.OutlinedButton(content="Volver a los módulos", on_click=self.cargar)]
        if evaluable:
            acciones.append(
                ft.FilledButton(content="Presentar evaluación", icon=ft.Icons.QUIZ_OUTLINED,
                                on_click=lambda: self.evaluar(modulo))
            )
        self.mostrar(
            self._volver(modulo.titulo, self.cargar),
            ft.Row([insignia(modulo.tema, tema.PRIMARIO, tema.PRIMARIO_SUAVE),
                    insignia(modulo.tipo_contenido, tema.INFO, tema.INFO_SUAVE)], spacing=8),
            tarjeta(
                ft.Markdown(
                    value=modulo.contenido,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                ),
                padding=28,
            ),
            ft.Row(acciones, alignment=ft.MainAxisAlignment.END, spacing=12),
        )

    def evaluar(self, modulo: ModuloEducativo) -> None:
        preguntas = self.sistema.evaluaciones.preguntas(modulo.id_modulo)
        respuestas: dict[int, int] = {}

        def responder(pregunta: Pregunta, grupo: ft.RadioGroup) -> None:
            respuestas[pregunta.id_pregunta] = int(grupo.value)

        def enviar() -> None:
            try:
                evaluacion = self.sistema.evaluaciones.calificar(self.usuario, modulo.id_modulo, respuestas)
            except ErrorAplicacion as error:
                self.app.notificar(str(error), error=True)
                return
            self.resultado(modulo, preguntas, respuestas, evaluacion)

        bloques: list[ft.Control] = []
        for numero, pregunta in enumerate(preguntas, start=1):
            grupo = ft.RadioGroup(
                content=ft.Column(
                    [ft.Radio(value=str(i), label=opcion) for i, opcion in enumerate(pregunta.opciones)],
                    spacing=2,
                ),
            )
            grupo.on_change = lambda e, p=pregunta: responder(p, e.control)
            bloques.append(
                tarjeta(
                    ft.Column(
                        [ft.Text(f"{numero}. {pregunta.enunciado}", size=15, weight=ft.FontWeight.W_600,
                                 color=tema.TEXTO), grupo],
                        spacing=10,
                    )
                )
            )

        self.mostrar(
            self._volver(f"Evaluación · {modulo.titulo}", lambda: self.abrir(modulo)),
            aviso("Necesitas 70 % o más para aprobar. Puedes presentarla cuantas veces quieras."),
            *bloques,
            ft.Row(
                [ft.FilledButton(content="Enviar respuestas", icon=ft.Icons.SEND, on_click=enviar)],
                alignment=ft.MainAxisAlignment.END,
            ),
        )

    def resultado(self, modulo: ModuloEducativo, preguntas: list[Pregunta], respuestas: dict[int, int],
                  evaluacion: Evaluacion) -> None:
        color, fondo = (tema.PRIMARIO, tema.PRIMARIO_SUAVE) if evaluacion.aprobada else (tema.AVISO, tema.AVISO_SUAVE)
        detalle: list[ft.Control] = [subtitulo("Revisión de respuestas")]
        for pregunta in preguntas:
            acierto = respuestas[pregunta.id_pregunta] == pregunta.respuesta
            detalle.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE if acierto else ft.Icons.CANCEL,
                                color=tema.PRIMARIO if acierto else tema.PELIGRO, size=20),
                        ft.Column(
                            [
                                ft.Text(pregunta.enunciado, size=14, weight=ft.FontWeight.W_500, color=tema.TEXTO),
                                ft.Text(f"Respuesta correcta: {pregunta.opciones[pregunta.respuesta]}",
                                        size=13, color=tema.TEXTO_SECUNDARIO),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=12,
                )
            )

        self.mostrar(
            self._volver(f"Resultado · {modulo.titulo}", self.cargar),
            tarjeta(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(f"{evaluacion.porcentaje} %", size=28, weight=ft.FontWeight.W_700,
                                            color=color),
                            width=110,
                            height=110,
                            border_radius=55,
                            bgcolor=fondo,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text("¡Módulo aprobado!" if evaluacion.aprobada else "Sigue intentándolo",
                                        size=20, weight=ft.FontWeight.W_700, color=tema.TEXTO),
                                ft.Text(f"Respondiste bien {evaluacion.aciertos} de {evaluacion.total} preguntas.",
                                        size=14, color=tema.TEXTO_SECUNDARIO),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    spacing=24,
                ),
                padding=24,
            ),
            tarjeta(ft.Column(detalle, spacing=14)),
            ft.Row(
                [
                    ft.OutlinedButton(content="Repasar el módulo", on_click=lambda: self.abrir(modulo)),
                    ft.OutlinedButton(content="Intentar de nuevo", icon=ft.Icons.REPLAY,
                                      on_click=lambda: self.evaluar(modulo)),
                    ft.FilledButton(content="Ver todos los módulos", on_click=self.cargar),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=12,
            ),
        )
