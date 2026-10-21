import flet as ft

from ....nucleo import ErrorAplicacion
from ....nucleo.entidades import TIPOS_METODO, Frecuencia, MetodoAnticonceptivo
from ....nucleo.servicios import decimal_opcional
from ... import tema
from ...componentes import (
    campo,
    celda,
    encabezado,
    formulario,
    insignia,
    mensaje_error,
    mostrar_error,
    selector,
    tabla,
    tarjeta,
    vacio,
)
from ...formato import efectividad
from ..base import Seccion


class GestionMetodos(Seccion):
    def cargar(self) -> None:
        metodos = self.sistema.contenido.listar_metodos()
        self.mostrar(
            encabezado(
                "Métodos anticonceptivos",
                "Administra el catálogo y los criterios que usa la orientación personalizada.",
                [ft.FilledButton(content="Nuevo método", icon=ft.Icons.ADD, on_click=lambda: self._editar(None))],
            ),
            tarjeta(
                tabla(
                    ["Método", "Tipo", "Efectividad", "Frecuencia", "Hormonal", "Protege ITS", "Acciones"],
                    [self._fila(m) for m in metodos],
                )
                if metodos
                else vacio(ft.Icons.MEDICATION_OUTLINED, "El catálogo está vacío."),
                padding=8,
            ),
        )

    def _fila(self, metodo: MetodoAnticonceptivo) -> list[ft.Control]:
        def marca(valor: bool) -> ft.Icon:
            return ft.Icon(ft.Icons.CHECK_CIRCLE if valor else ft.Icons.REMOVE,
                           color=tema.PRIMARIO if valor else tema.BORDE, size=20)

        return [
            celda(metodo.nombre, negrita=True, ancho=200),
            insignia(metodo.tipo, *tema.COLORES_TIPO.get(metodo.tipo, (tema.PRIMARIO, tema.PRIMARIO_SUAVE))),
            celda(efectividad(metodo.efectividad)),
            celda(metodo.frecuencia),
            marca(metodo.hormonal),
            marca(metodo.protege_its),
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip="Editar", icon_color=tema.INFO,
                                  on_click=lambda: self._editar(metodo)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", icon_color=tema.PELIGRO,
                                  on_click=lambda: self._eliminar(metodo)),
                ],
                spacing=0,
            ),
        ]

    def _editar(self, metodo: MetodoAnticonceptivo | None) -> None:
        nombre = campo("Nombre", metodo.nombre if metodo else "")
        tipo = selector("Tipo", [(t, t) for t in TIPOS_METODO], metodo.tipo if metodo else None, expand=True)
        frecuencia = selector("Frecuencia de uso", [(f.value, f.value) for f in Frecuencia],
                              metodo.frecuencia.value if metodo else None, expand=True)
        valor_efectividad = campo(
            "Efectividad en uso típico (%)",
            "" if metodo is None or metodo.efectividad is None else f"{metodo.efectividad:g}",
            helper="Déjalo vacío para métodos de uso ocasional.",
        )
        descripcion = campo("Descripción", metodo.descripcion if metodo else "", multiline=True,
                            min_lines=3, max_lines=5)
        indicado = campo("Indicado para", metodo.indicado_para if metodo else "", multiline=True,
                         min_lines=2, max_lines=4)
        hormonal = ft.Switch(label="Es hormonal", value=metodo.hormonal if metodo else False)
        estrogeno = ft.Switch(label="Contiene estrógeno", value=metodo.con_estrogeno if metodo else False)
        its = ft.Switch(label="Protege frente a ITS", value=metodo.protege_its if metodo else False)
        error = mensaje_error()

        def guardar() -> None:
            try:
                self.sistema.contenido.guardar_metodo(
                    self.usuario,
                    MetodoAnticonceptivo(
                        metodo.id_metodo if metodo else None,
                        nombre.value,
                        tipo.value,
                        decimal_opcional(valor_efectividad.value, "Efectividad"),
                        frecuencia.value,
                        descripcion.value,
                        indicado.value,
                        hormonal.value,
                        estrogeno.value,
                        its.value,
                    ),
                )
            except ErrorAplicacion as fallo:
                mostrar_error(error, str(fallo))
                return
            self.app.cerrar_dialogo()
            self.cargar()
            self.app.notificar("Método guardado.")

        self.app.abrir_dialogo(
            "Editar método" if metodo else "Nuevo método",
            formulario(
                nombre,
                ft.Row([tipo, frecuencia], spacing=12),
                valor_efectividad,
                descripcion,
                indicado,
                ft.Row([hormonal, estrogeno, its], wrap=True, spacing=20),
                error,
            ),
            [
                ft.TextButton(content="Cancelar", on_click=self.app.cerrar_dialogo),
                ft.FilledButton(content="Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=guardar),
            ],
            ancho=620,
        )

    def _eliminar(self, metodo: MetodoAnticonceptivo) -> None:
        def ejecutar() -> None:
            self.sistema.contenido.eliminar_metodo(self.usuario, metodo.id_metodo)
            self.cargar()
            self.app.notificar("Método eliminado del catálogo.")

        self.app.confirmar("Eliminar método", f"¿Eliminar «{metodo.nombre}» del catálogo?", ejecutar, "Eliminar")
