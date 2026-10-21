import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import PerfilOrientacion, Recomendacion
from ... import tema
from ...componentes import aviso, encabezado, insignia, subtitulo, tarjeta, vacio
from ...formato import fecha_hora
from ..base import Seccion

PREGUNTAS = (
    ("recuerda_diario", "¿Te resulta fácil recordar algo todos los días a la misma hora?",
     (("si", "Sí, tengo una rutina estable"), ("no", "No, suelo olvidarlo"))),
    ("horizonte", "¿Por cuánto tiempo quieres evitar un embarazo?",
     (("corto", "Menos de un año"), ("medio", "Entre uno y tres años"), ("largo", "Más de tres años"))),
    ("acepta_hormonas", "¿Cómo te sientes con los métodos hormonales?",
     (("si", "Los acepto"), ("no", "Prefiero evitarlos"), ("nose", "Aún no lo sé"))),
    ("pareja_estable", "¿Tienes una pareja estable y ambos se hicieron pruebas de ITS recientemente?",
     (("si", "Sí"), ("no", "No, o no lo sé"))),
    ("restriccion_estrogeno",
     "¿Tienes migraña con aura, presión arterial alta, fumas o tuviste un parto hace menos de seis semanas?",
     (("si", "Sí, alguna de ellas"), ("no", "No"))),
)

BOOLEANAS = {"recuerda_diario", "pareja_estable", "restriccion_estrogeno"}


class Orientacion(Seccion):
    def cargar(self) -> None:
        self.panel = ft.Container(col={"xs": 12, "lg": 7})
        self.historial = ft.Container(col={"xs": 12, "lg": 5})
        self._cuestionario()
        self._historial()
        self.mostrar(
            encabezado("Orientación personalizada",
                       "Responde unas preguntas y recibe opciones de métodos acordes a tu situación."),
            ft.ResponsiveRow([self.panel, self.historial], spacing=16, run_spacing=16,
                             vertical_alignment=ft.CrossAxisAlignment.START),
        )

    def _cuestionario(self) -> None:
        respuestas: dict[str, str] = {}
        error = ft.Text("", color=tema.PELIGRO, size=13, visible=False)
        bloques: list[ft.Control] = []

        def elegir(clave: str, valor: str) -> None:
            respuestas[clave] = valor
            error.visible = False

        for numero, (clave, enunciado, opciones) in enumerate(PREGUNTAS, start=1):
            grupo = ft.RadioGroup(
                content=ft.Column([ft.Radio(value=valor, label=texto) for valor, texto in opciones], spacing=0),
                on_change=lambda e, c=clave: elegir(c, e.control.value),
            )
            bloques.append(
                ft.Column(
                    [ft.Text(f"{numero}. {enunciado}", size=14, weight=ft.FontWeight.W_600, color=tema.TEXTO), grupo],
                    spacing=6,
                )
            )

        def enviar() -> None:
            if len(respuestas) < len(PREGUNTAS):
                error.value = "Responde todas las preguntas para recibir tu orientación."
                error.visible = True
                return
            perfil = PerfilOrientacion(
                **{c: (v == "si") if c in BOOLEANAS else v for c, v in respuestas.items()}
            )
            try:
                recomendaciones = self.sistema.orientacion.recomendar(self.usuario, perfil)
            except ErrorAplicacion as fallo:
                error.value = str(fallo)
                error.visible = True
                return
            self._resultados(recomendaciones)
            self._historial()

        self.panel.content = tarjeta(
            ft.Column(
                [
                    subtitulo("Cuestionario"),
                    ft.Text("Tus respuestas son privadas y solo se usan para darte esta orientación.",
                            size=13, color=tema.TEXTO_SECUNDARIO),
                    ft.Divider(height=1, color=tema.BORDE),
                    *bloques,
                    error,
                    ft.Row(
                        [ft.FilledButton(content="Ver mis opciones", icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                                         on_click=enviar)],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=16,
            ),
            padding=24,
        )

    def _resultados(self, recomendaciones: list[Recomendacion]) -> None:
        tarjetas = [self._recomendacion(posicion, r) for posicion, r in enumerate(recomendaciones, start=1)]
        self.panel.content = ft.Column(
            [
                tarjeta(
                    ft.Column(
                        [
                            subtitulo("Opciones sugeridas para ti"),
                            ft.Text("Ordenadas según tus respuestas. Llévalas a tu cita para decidir con el "
                                    "personal de salud.", size=13, color=tema.TEXTO_SECUNDARIO),
                        ],
                        spacing=4,
                    )
                ),
                *(tarjetas or [tarjeta(vacio(ft.Icons.SEARCH_OFF,
                                             "No encontramos opciones con tus respuestas. Agenda una asesoría."))]),
                aviso("Esta orientación es educativa y no reemplaza la valoración del personal de salud.",
                      ft.Icons.MEDICAL_INFORMATION_OUTLINED, tema.AVISO, tema.AVISO_SUAVE),
                ft.Row(
                    [
                        ft.OutlinedButton(content="Responder de nuevo", icon=ft.Icons.REPLAY,
                                          on_click=self._cuestionario),
                        ft.FilledButton(content="Agendar asesoría", icon=ft.Icons.EVENT,
                                        on_click=lambda: self.app.ir_a("citas")),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=12,
                ),
            ],
            spacing=14,
        )

    @staticmethod
    def _recomendacion(posicion: int, recomendacion: Recomendacion) -> ft.Container:
        metodo = recomendacion.metodo
        color, fondo = tema.COLORES_TIPO.get(metodo.tipo, (tema.PRIMARIO, tema.PRIMARIO_SUAVE))
        return tarjeta(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(str(posicion), size=18, weight=ft.FontWeight.W_700, color=color),
                        width=42,
                        height=42,
                        border_radius=21,
                        bgcolor=fondo,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [ft.Text(metodo.nombre, size=16, weight=ft.FontWeight.W_600, color=tema.TEXTO),
                                 insignia(metodo.tipo, color, fondo)],
                                spacing=10,
                                wrap=True,
                            ),
                            *[
                                ft.Row(
                                    [ft.Icon(ft.Icons.CHECK, size=16, color=tema.PRIMARIO),
                                     ft.Text(motivo, size=13, color=tema.TEXTO_SECUNDARIO, expand=True)],
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                )
                                for motivo in recomendacion.motivos
                            ],
                        ],
                        spacing=6,
                        expand=True,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    def _historial(self) -> None:
        registros = self.sistema.orientacion.historial(self.usuario)
        if registros:
            filas: list[ft.Control] = [
                ft.Column(
                    [
                        ft.Text(fecha_hora(r.fecha), size=12, color=tema.TEXTO_SECUNDARIO),
                        ft.Row([insignia(n, tema.PRIMARIO, tema.PRIMARIO_SUAVE) for n in r.recomendados],
                               wrap=True, spacing=6, run_spacing=6),
                    ],
                    spacing=6,
                )
                for r in registros[:6]
            ]
        else:
            filas = [vacio(ft.Icons.HISTORY, "Aquí verás el seguimiento de tus orientaciones.")]
        self.historial.content = tarjeta(
            ft.Column([subtitulo("Seguimiento"), *filas], spacing=16),
            padding=24,
        )
