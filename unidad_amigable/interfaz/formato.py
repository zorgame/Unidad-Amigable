from datetime import date, datetime

DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


def fecha_larga(valor: date) -> str:
    return f"{DIAS[valor.weekday()].capitalize()} {valor.day} de {MESES[valor.month - 1]}"


def fecha_corta(valor: date) -> str:
    return f"{valor.day:02d} {MESES[valor.month - 1][:3]} {valor.year}"


def fecha_hora(valor: datetime) -> str:
    return f"{fecha_corta(valor)} · {valor:%H:%M}"


def hora_legible(hora: str) -> str:
    horas, minutos = map(int, hora.split(":"))
    sufijo = "a. m." if horas < 12 else "p. m."
    return f"{(horas - 1) % 12 + 1}:{minutos:02d} {sufijo}"


def efectividad(valor: float | None) -> str:
    return "Uso ocasional" if valor is None else f"{valor:g} %"


def iniciales(nombre: str) -> str:
    partes = nombre.split()
    return "".join(p[0] for p in partes[:2]).upper() or "?"


def primer_nombre(nombre: str) -> str:
    return nombre.split()[0] if nombre.split() else nombre
