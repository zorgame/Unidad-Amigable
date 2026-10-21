import flet as ft

from ....nucleo.entidades import TIPOS_METODO, MetodoAnticonceptivo
from ... import tema
from ...componentes import aviso, campo, encabezado, insignia, subtitulo, tarjeta, vacio
from ...formato import efectividad
from ..base import Seccion

TODOS = "todos"


class Metodos(Seccion):
    def cargar(self) -> None:
        self.tipo = TODOS
        self.grilla = ft.ResponsiveRow(spacing=16, run_spacing=16)
        self.busqueda = campo("Buscar método", icono=ft.Icons.SEARCH, on_change=self._filtrar)
        filtros = ft.SegmentedButton(
            segments=[ft.Segment(value=TODOS, label="Todos"),
                      *[ft.Segment(value=t, label=t) for t in TIPOS_METODO]],
            selected=[TODOS],
            show_selected_icon=False,
            on_change=self._cambiar_tipo,
        )
        self._filtrar()
        self.mostrar(
            encabezado("Métodos anticonceptivos",
                       "Conoce cómo funciona cada método, su efectividad real y para quién está indicado."),
            aviso("Solo el condón (masculino o femenino) protege frente a las infecciones de transmisión sexual. "
                  "Combínalo con otro método para tener doble protección.",
                  ft.Icons.SHIELD_OUTLINED, tema.PRIMARIO, tema.PRIMARIO_SUAVE),
            ft.ResponsiveRow(
                [
                    ft.Container(filtros, col={"xs": 12, "xl": 8}),
                    ft.Container(self.busqueda, col={"xs": 12, "xl": 4}),
                ],
                spacing=12,
                run_spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            self.grilla,
        )

    def _cambiar_tipo(self, e: ft.Event[ft.SegmentedButton]) -> None:
        self.tipo = e.control.selected[0]
        self._filtrar()

    def _filtrar(self) -> None:
        metodos = self.sistema.contenido.listar_metodos(
            None if self.tipo == TODOS else self.tipo, self.busqueda.value or ""
        )
        self.grilla.controls = [self._tarjeta(m) for m in metodos] or [
            ft.Container(vacio(ft.Icons.SEARCH_OFF, "No encontramos métodos con ese filtro."), col=12)
        ]

    def _tarjeta(self, metodo: MetodoAnticonceptivo) -> ft.Container:
        color, fondo = tema.COLORES_TIPO.get(metodo.tipo, (tema.PRIMARIO, tema.PRIMARIO_SUAVE))
        proporcion = (metodo.efectividad or 0) / 100
        return tarjeta(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(metodo.nombre, size=16, weight=ft.FontWeight.W_600, color=tema.TEXTO,
                                    expand=True),
                            insignia(metodo.tipo, color, fondo),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Row(
                        [
                            ft.Text("Efectividad", size=12, color=tema.TEXTO_SECUNDARIO, expand=True),
                            ft.Text(efectividad(metodo.efectividad), size=13, weight=ft.FontWeight.W_700,
                                    color=color),
                        ]
                    ),
                    ft.ProgressBar(value=proporcion, color=color, bgcolor=fondo, bar_height=6, border_radius=3),
                    self._dato(ft.Icons.SCHEDULE, metodo.frecuencia),
                    self._dato(
                        ft.Icons.VERIFIED_USER_OUTLINED if metodo.protege_its else ft.Icons.REMOVE_MODERATOR_OUTLINED,
                        "Protege frente a ITS" if metodo.protege_its else "No protege frente a ITS",
                        tema.PRIMARIO if metodo.protege_its else tema.TEXTO_SECUNDARIO,
                    ),
                    ft.Row(
                        [ft.TextButton(content="Ver detalle", icon=ft.Icons.INFO_OUTLINE,
                                       on_click=lambda: self._detalle(metodo))],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=10,
            ),
            col={"xs": 12, "md": 6, "xl": 4},
            on_click=lambda: self._detalle(metodo),
        )

    @staticmethod
    def _dato(icono: ft.IconData, texto: str, color: str = tema.TEXTO_SECUNDARIO) -> ft.Row:
        return ft.Row([ft.Icon(icono, size=18, color=color), ft.Text(texto, size=13, color=color)], spacing=8)

    def _detalle(self, metodo: MetodoAnticonceptivo) -> None:
        color, fondo = tema.COLORES_TIPO.get(metodo.tipo, (tema.PRIMARIO, tema.PRIMARIO_SUAVE))
        caracteristicas = [
            insignia(metodo.tipo, color, fondo),
            insignia(metodo.frecuencia, tema.TEXTO_SECUNDARIO, tema.FONDO, ft.Icons.SCHEDULE),
        ]
        if metodo.tipo != "Hormonal":
            caracteristicas.append(
                insignia("Con hormonas" if metodo.hormonal else "Sin hormonas", tema.TEXTO_SECUNDARIO, tema.FONDO)
            )
        if metodo.con_estrogeno:
            caracteristicas.append(insignia("Contiene estrógeno", tema.AVISO, tema.AVISO_SUAVE))
        self.app.abrir_dialogo(
            metodo.nombre,
            ft.Column(
                [
                    ft.Row(caracteristicas, wrap=True, spacing=8, run_spacing=8),
                    subtitulo("¿Cómo funciona?"),
                    ft.Text(metodo.descripcion, size=14, color=tema.TEXTO),
                    subtitulo("¿Para quién está indicado?"),
                    ft.Text(metodo.indicado_para, size=14, color=tema.TEXTO),
                    subtitulo("Efectividad en uso típico"),
                    ft.Text(efectividad(metodo.efectividad), size=14, color=tema.TEXTO),
                    aviso("Consulta con el personal de salud antes de iniciar o cambiar un método."),
                ],
                spacing=10,
                tight=True,
            ),
            [
                ft.TextButton(content="Cerrar", on_click=self.app.cerrar_dialogo),
                ft.FilledButton(content="Agendar asesoría", icon=ft.Icons.EVENT, on_click=self._agendar),
            ],
            ancho=520,
        )

    def _agendar(self) -> None:
        self.app.cerrar_dialogo()
        self.app.ir_a("citas")
        self.app.page.update()
