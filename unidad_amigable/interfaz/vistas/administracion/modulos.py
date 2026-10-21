import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import TIPOS_CONTENIDO, ModuloEducativo
from ... import tema
from ...componentes import (
    campo,
    encabezado,
    formulario,
    icono_circular,
    insignia,
    mensaje_error,
    mostrar_error,
    selector,
    tarjeta,
    vacio,
)
from ..base import Seccion


class GestionModulos(Seccion):
    def cargar(self) -> None:
        modulos = self.sistema.contenido.listar_modulos()
        evaluables = self.sistema.contenido.modulos_evaluables()
        self.mostrar(
            encabezado(
                "Módulos educativos",
                "Crea y actualiza el contenido que consultan los estudiantes.",
                [ft.FilledButton(content="Nuevo módulo", icon=ft.Icons.ADD, on_click=lambda: self._editar(None))],
            ),
            *([self._fila(m, m.id_modulo in evaluables) for m in modulos]
              or [tarjeta(vacio(ft.Icons.LIBRARY_BOOKS_OUTLINED, "No hay módulos publicados."))]),
        )

    def _fila(self, modulo: ModuloEducativo, evaluable: bool) -> ft.Container:
        return tarjeta(
            ft.Row(
                [
                    icono_circular(ft.Icons.MENU_BOOK_OUTLINED),
                    ft.Column(
                        [
                            ft.Text(modulo.titulo, size=15, weight=ft.FontWeight.W_600, color=tema.TEXTO),
                            ft.Row(
                                [
                                    insignia(modulo.tema, tema.PRIMARIO, tema.PRIMARIO_SUAVE),
                                    insignia(modulo.tipo_contenido, tema.INFO, tema.INFO_SUAVE),
                                    insignia("Con evaluación" if evaluable else "Sin evaluación",
                                             tema.TEXTO_SECUNDARIO, tema.FONDO,
                                             ft.Icons.QUIZ_OUTLINED if evaluable else None),
                                ],
                                spacing=6,
                                wrap=True,
                            ),
                        ],
                        spacing=6,
                        expand=True,
                    ),
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip="Editar", icon_color=tema.INFO,
                                  on_click=lambda: self._editar(modulo)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", icon_color=tema.PELIGRO,
                                  on_click=lambda: self._eliminar(modulo)),
                ],
                spacing=16,
            ),
            padding=16,
        )

    def _editar(self, modulo: ModuloEducativo | None) -> None:
        titulo = campo("Título", modulo.titulo if modulo else "")
        tema_modulo = campo("Tema", modulo.tema if modulo else "", expand=True)
        tipo = selector("Tipo de contenido", [(t, t) for t in TIPOS_CONTENIDO],
                        modulo.tipo_contenido if modulo else TIPOS_CONTENIDO[0], expand=True)
        contenido = campo("Contenido", modulo.contenido if modulo else "", multiline=True, min_lines=10,
                          max_lines=14, helper="Admite formato Markdown: ## títulos, **negrita**, listas con -.")
        error = mensaje_error()

        def guardar() -> None:
            try:
                self.sistema.contenido.guardar_modulo(
                    self.usuario, modulo.id_modulo if modulo else None,
                    titulo.value, tema_modulo.value, contenido.value, tipo.value,
                )
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            self.app.cerrar_dialogo()
            self.cargar()
            self.app.notificar("Módulo guardado.")

        self.app.abrir_dialogo(
            "Editar módulo" if modulo else "Nuevo módulo",
            formulario(titulo, ft.Row([tema_modulo, tipo], spacing=12), contenido, error),
            [
                ft.TextButton(content="Cancelar", on_click=self.app.cerrar_dialogo),
                ft.FilledButton(content="Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=guardar),
            ],
            ancho=640,
        )

    def _eliminar(self, modulo: ModuloEducativo) -> None:
        def ejecutar() -> None:
            self.sistema.contenido.eliminar_modulo(self.usuario, modulo.id_modulo)
            self.cargar()
            self.app.notificar("Módulo eliminado.")

        self.app.confirmar(
            "Eliminar módulo",
            f"Se eliminará «{modulo.titulo}» junto con sus preguntas y los resultados de evaluación.",
            ejecutar,
            "Eliminar",
        )
