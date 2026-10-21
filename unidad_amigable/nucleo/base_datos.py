import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE COLLATE NOCASE,
    contrasena TEXT NOT NULL,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('estudiante', 'administrador')),
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS estudiantes (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    codigo TEXT NOT NULL UNIQUE,
    programa_academico TEXT NOT NULL,
    semestre INTEGER NOT NULL CHECK (semestre BETWEEN 1 AND 12),
    edad INTEGER NOT NULL CHECK (edad BETWEEN 14 AND 99)
);

CREATE TABLE IF NOT EXISTS administradores (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    cargo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unidades (
    id_unidad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    ubicacion TEXT NOT NULL,
    contacto TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS modulos (
    id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    tema TEXT NOT NULL,
    contenido TEXT NOT NULL,
    tipo_contenido TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS preguntas (
    id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_modulo INTEGER NOT NULL REFERENCES modulos (id_modulo) ON DELETE CASCADE,
    enunciado TEXT NOT NULL,
    opciones TEXT NOT NULL,
    respuesta INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluaciones (
    id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    id_modulo INTEGER NOT NULL REFERENCES modulos (id_modulo) ON DELETE CASCADE,
    aciertos INTEGER NOT NULL,
    total INTEGER NOT NULL,
    fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS metodos (
    id_metodo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE COLLATE NOCASE,
    tipo TEXT NOT NULL,
    efectividad REAL,
    frecuencia TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    indicado_para TEXT NOT NULL,
    hormonal INTEGER NOT NULL DEFAULT 0,
    con_estrogeno INTEGER NOT NULL DEFAULT 0,
    protege_its INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS citas (
    id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    id_unidad INTEGER NOT NULL REFERENCES unidades (id_unidad),
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('Pendiente', 'Confirmada', 'Atendida', 'Cancelada')),
    motivo TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_citas_franja
    ON citas (id_unidad, fecha, hora) WHERE estado <> 'Cancelada';

CREATE TABLE IF NOT EXISTS orientaciones (
    id_orientacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    respuestas TEXT NOT NULL,
    recomendados TEXT NOT NULL
);
"""


class BaseDatos:
    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta
        self.ruta.parent.mkdir(parents=True, exist_ok=True)

    def _conectar(self) -> sqlite3.Connection:
        conexion = sqlite3.connect(self.ruta)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    @contextmanager
    def sesion(self) -> Iterator[sqlite3.Connection]:
        conexion = self._conectar()
        try:
            with conexion:
                yield conexion
        finally:
            conexion.close()

    def inicializar(self) -> None:
        with self.sesion() as conexion:
            conexion.executescript(ESQUEMA)
