from collections.abc import Callable, Iterable

import flet as ft

from . import tema


def tarjeta(
    contenido: ft.Control,
    padding: int = 20,
    col: dict | None = None,
    on_click: Callable | None = None,
    bgcolor: str = tema.SUPERFICIE,
    expand: bool | int | None = None,
) -> ft.Container:
    return ft.Container(
        content=contenido,
        padding=padding,
        bgcolor=bgcolor,
        border_radius=tema.RADIO,
        border=ft.Border.all(1, tema.BORDE),
        col=col,
        on_click=on_click,
        ink=on_click is not None,
        expand=expand,
    )


def encabezado(titulo: str, descripcion: str, acciones: list[ft.Control] | None = None) -> ft.Row:
    return ft.Row(
        [
            ft.Column(
                [
                    ft.Text(titulo, size=26, weight=ft.FontWeight.W_700, color=tema.TEXTO),
                    ft.Text(descripcion, size=14, color=tema.TEXTO_SECUNDARIO),
                ],
                spacing=4,
                expand=True,
            ),
            *(acciones or []),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def subtitulo(texto: str) -> ft.Text:
    return ft.Text(texto, size=16, weight=ft.FontWeight.W_600, color=tema.TEXTO)


def insignia(texto: str, color: str, fondo: str, icono: ft.IconData | None = None) -> ft.Container:
    contenido: list[ft.Control] = [ft.Text(texto, size=12, weight=ft.FontWeight.W_600, color=color)]
    if icono:
        contenido.insert(0, ft.Icon(icono, size=14, color=color))
    return ft.Container(
        content=ft.Row(contenido, spacing=4, tight=True),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=fondo,
        border_radius=20,
    )


def icono_circular(icono: ft.IconData, color: str = tema.PRIMARIO, fondo: str = tema.PRIMARIO_SUAVE,
                   tamano: int = 44) -> ft.Container:
    return ft.Container(
        content=ft.Icon(icono, color=color, size=tamano * 0.5),
        width=tamano,
        height=tamano,
        bgcolor=fondo,
        border_radius=tamano / 2,
        alignment=ft.Alignment.CENTER,
    )


def indicador(icono: ft.IconData, valor: str, etiqueta: str, color: str = tema.PRIMARIO,
              fondo: str = tema.PRIMARIO_SUAVE, col: dict | None = None) -> ft.Container:
    return tarjeta(
        ft.Row(
            [
                icono_circular(icono, color, fondo, 48),
                ft.Column(
                    [
                        ft.Text(valor, size=22, weight=ft.FontWeight.W_700, color=tema.TEXTO,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(etiqueta, size=13, color=tema.TEXTO_SECUNDARIO),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ],
            spacing=14,
        ),
        padding=18,
        col=col,
    )


def aviso(texto: str, icono: ft.IconData = ft.Icons.INFO_OUTLINE, color: str = tema.INFO,
          fondo: str = tema.INFO_SUAVE) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [ft.Icon(icono, color=color, size=20), ft.Text(texto, size=13, color=tema.TEXTO, expand=True)],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=14,
        bgcolor=fondo,
        border_radius=10,
    )


def vacio(icono: ft.IconData, mensaje: str, accion: ft.Control | None = None) -> ft.Container:
    contenido: list[ft.Control] = [
        ft.Icon(icono, size=48, color=tema.BORDE),
        ft.Text(mensaje, size=14, color=tema.TEXTO_SECUNDARIO, text_align=ft.TextAlign.CENTER),
    ]
    if accion:
        contenido.append(accion)
    return ft.Container(
        content=ft.Column(contenido, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
        padding=40,
        alignment=ft.Alignment.CENTER,
    )


def borde_campo() -> dict[ft.ControlState, ft.OutlineInputBorder]:
    return {
        ft.ControlState.DEFAULT: ft.OutlineInputBorder(border_radius=10, side=ft.BorderSide(1, tema.BORDE)),
        ft.ControlState.FOCUSED: ft.OutlineInputBorder(border_radius=10, side=ft.BorderSide(2, tema.PRIMARIO)),
    }


def campo(etiqueta: str, valor: str = "", icono: ft.IconData | None = None, **opciones) -> ft.TextField:
    return ft.TextField(
        label=etiqueta,
        value=valor,
        prefix_icon=icono,
        border=borde_campo(),
        align_label_with_hint=opciones.get("multiline", False),
        filled=True,
        fill_color=tema.SUPERFICIE,
        text_size=14,
        **opciones,
    )


def selector(etiqueta: str, opciones: Iterable[tuple[str, str]], valor: str | None = None,
             icono: ft.IconData | None = None, **extra) -> ft.Dropdown:
    return ft.Dropdown(
        label=etiqueta,
        value=valor,
        options=[ft.DropdownOption(key=clave, text=texto) for clave, texto in opciones],
        leading_icon=icono,
        border=borde_campo(),
        filled=True,
        fill_color=tema.SUPERFICIE,
        text_size=14,
        **extra,
    )


def barra(etiqueta: str, detalle: str, proporcion: float, color: str = tema.PRIMARIO) -> ft.Column:
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text(etiqueta, size=13, color=tema.TEXTO, expand=True,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(detalle, size=13, weight=ft.FontWeight.W_600, color=tema.TEXTO_SECUNDARIO),
                ]
            ),
            ft.ProgressBar(value=max(0.0, min(proporcion, 1.0)), color=color, bgcolor=tema.PRIMARIO_SUAVE,
                           bar_height=8, border_radius=4),
        ],
        spacing=6,
    )


def tabla(columnas: list[str], filas: list[list[ft.Control]]) -> ft.Row:
    return ft.Row(
        [
            ft.DataTable(
                columns=[
                    ft.DataColumn(label=ft.Text(c, weight=ft.FontWeight.W_600, color=tema.TEXTO_SECUNDARIO, size=13))
                    for c in columnas
                ],
                rows=[ft.DataRow(cells=[ft.DataCell(content=celda) for celda in fila]) for fila in filas],
                heading_row_color=tema.FONDO,
                heading_row_height=44,
                data_row_min_height=52,
                data_row_max_height=64,
                column_spacing=22,
                divider_thickness=0.6,
                horizontal_margin=16,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
    )


def celda(texto: str, negrita: bool = False, ancho: int | None = None) -> ft.Text:
    return ft.Text(
        texto,
        size=13,
        color=tema.TEXTO,
        weight=ft.FontWeight.W_600 if negrita else None,
        width=ancho,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )


def celda_doble(principal: str, secundario: str, ancho: int = 200) -> ft.Column:
    return ft.Column(
        [
            ft.Text(principal, size=13, weight=ft.FontWeight.W_600, color=tema.TEXTO, width=ancho,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            ft.Text(secundario, size=12, color=tema.TEXTO_SECUNDARIO, width=ancho,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        ],
        spacing=2,
        alignment=ft.MainAxisAlignment.CENTER,
    )


def formulario(*controles: ft.Control, espacio: int = 16) -> ft.Column:
    return ft.Column(list(controles), spacing=espacio, tight=True,
                     horizontal_alignment=ft.CrossAxisAlignment.STRETCH)


def mensaje_error() -> ft.Text:
    return ft.Text("", color=tema.PELIGRO, size=13, visible=False)


def mostrar_error(control: ft.Text, mensaje: str) -> None:
    control.value = mensaje
    control.visible = True
