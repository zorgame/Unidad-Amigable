from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum


class TipoUsuario(StrEnum):
    ESTUDIANTE = "estudiante"
    ADMINISTRADOR = "administrador"


class EstadoCita(StrEnum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    ATENDIDA = "Atendida"
    CANCELADA = "Cancelada"


class Frecuencia(StrEnum):
    DIARIA = "Diaria"
    SEMANAL = "Semanal"
    MENSUAL = "Mensual"
    TRIMESTRAL = "Trimestral"
    VARIOS_ANIOS = "Varios años"
    CADA_RELACION = "En cada relación"
    OCASIONAL = "Ocasional"


TIPOS_METODO = ("Hormonal", "Intrauterino", "Barrera", "Emergencia")
TIPOS_CONTENIDO = ("Lectura", "Guía práctica", "Preguntas frecuentes")
MOTIVOS_CITA = (
    "Asesoría en anticoncepción",
    "Control del método actual",
    "Prevención y pruebas de ITS",
    "Anticoncepción de emergencia",
    "Orientación en salud sexual",
)


@dataclass(slots=True)
class Usuario:
    id_usuario: int
    nombre: str
    correo: str
    tipo_usuario: TipoUsuario

    @property
    def es_administrador(self) -> bool:
        return self.tipo_usuario is TipoUsuario.ADMINISTRADOR


@dataclass(slots=True)
class Estudiante(Usuario):
    codigo: str
    programa_academico: str
    semestre: int
    edad: int


@dataclass(slots=True)
class Administrador(Usuario):
    cargo: str


@dataclass(slots=True)
class UnidadAmigable:
    id_unidad: int
    nombre: str
    ubicacion: str
    contacto: str


@dataclass(slots=True)
class ModuloEducativo:
    id_modulo: int | None
    titulo: str
    tema: str
    contenido: str
    tipo_contenido: str


@dataclass(slots=True)
class Pregunta:
    id_pregunta: int | None
    id_modulo: int
    enunciado: str
    opciones: list[str]
    respuesta: int


@dataclass(slots=True)
class Evaluacion:
    id_evaluacion: int
    id_usuario: int
    id_modulo: int
    aciertos: int
    total: int
    fecha: datetime

    @property
    def porcentaje(self) -> int:
        return round(self.aciertos * 100 / self.total) if self.total else 0

    @property
    def aprobada(self) -> bool:
        return self.porcentaje >= 70


@dataclass(slots=True)
class MetodoAnticonceptivo:
    id_metodo: int | None
    nombre: str
    tipo: str
    efectividad: float | None
    frecuencia: Frecuencia
    descripcion: str
    indicado_para: str
    hormonal: bool = False
    con_estrogeno: bool = False
    protege_its: bool = False


@dataclass(slots=True)
class Cita:
    id_cita: int
    id_usuario: int
    id_unidad: int
    fecha: date
    hora: str
    estado: EstadoCita
    motivo: str
    estudiante: str = ""
    codigo: str = ""

    @property
    def activa(self) -> bool:
        return self.estado in (EstadoCita.PENDIENTE, EstadoCita.CONFIRMADA)


@dataclass(slots=True)
class PerfilOrientacion:
    recuerda_diario: bool
    horizonte: str
    acepta_hormonas: str
    pareja_estable: bool
    restriccion_estrogeno: bool


@dataclass(slots=True)
class Recomendacion:
    metodo: MetodoAnticonceptivo
    puntaje: float
    motivos: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Orientacion:
    id_orientacion: int
    id_usuario: int
    fecha: datetime
    recomendados: list[str]


@dataclass(slots=True)
class Resumen:
    estudiantes: int
    citas_pendientes: int
    citas_atendidas: int
    evaluaciones: int
    orientaciones: int
    rendimiento_modulos: list[tuple[str, int, int]]
    metodos_recomendados: list[tuple[str, int]]
