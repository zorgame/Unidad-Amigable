import json
import sqlite3
from datetime import date, datetime

from .base_datos import BaseDatos
from .entidades import (
    Administrador,
    Cita,
    Estudiante,
    EstadoCita,
    Evaluacion,
    Frecuencia,
    MetodoAnticonceptivo,
    ModuloEducativo,
    Orientacion,
    Pregunta,
    TipoUsuario,
    UnidadAmigable,
    Usuario,
)


class Repositorio:
    def __init__(self, bd: BaseDatos) -> None:
        self.bd = bd


class RepositorioUsuarios(Repositorio):
    CONSULTA = """
        SELECT u.id_usuario, u.nombre, u.correo, u.tipo_usuario, u.creado_en,
               e.codigo, e.programa_academico, e.semestre, e.edad, a.cargo
        FROM usuarios u
        LEFT JOIN estudiantes e ON e.id_usuario = u.id_usuario
        LEFT JOIN administradores a ON a.id_usuario = u.id_usuario
    """

    @staticmethod
    def _convertir(fila: sqlite3.Row) -> Usuario:
        tipo = TipoUsuario(fila["tipo_usuario"])
        base = (fila["id_usuario"], fila["nombre"], fila["correo"], tipo)
        if tipo is TipoUsuario.ADMINISTRADOR:
            return Administrador(*base, cargo=fila["cargo"] or "")
        return Estudiante(
            *base,
            codigo=fila["codigo"],
            programa_academico=fila["programa_academico"],
            semestre=fila["semestre"],
            edad=fila["edad"],
        )

    def obtener(self, id_usuario: int) -> Usuario | None:
        with self.bd.sesion() as c:
            fila = c.execute(f"{self.CONSULTA} WHERE u.id_usuario = ?", (id_usuario,)).fetchone()
        return self._convertir(fila) if fila else None

    def credenciales(self, correo: str) -> tuple[int, str] | None:
        with self.bd.sesion() as c:
            fila = c.execute(
                "SELECT id_usuario, contrasena FROM usuarios WHERE correo = ?", (correo,)
            ).fetchone()
        return (fila["id_usuario"], fila["contrasena"]) if fila else None

    def contrasena(self, id_usuario: int) -> str:
        with self.bd.sesion() as c:
            return c.execute(
                "SELECT contrasena FROM usuarios WHERE id_usuario = ?", (id_usuario,)
            ).fetchone()["contrasena"]

    def existe_correo(self, correo: str, excepto: int | None = None) -> bool:
        with self.bd.sesion() as c:
            fila = c.execute(
                "SELECT 1 FROM usuarios WHERE correo = ? AND id_usuario IS NOT ?", (correo, excepto)
            ).fetchone()
        return fila is not None

    def existe_codigo(self, codigo: str) -> bool:
        with self.bd.sesion() as c:
            return c.execute("SELECT 1 FROM estudiantes WHERE codigo = ?", (codigo,)).fetchone() is not None

    def crear_estudiante(
        self, nombre: str, correo: str, contrasena: str, codigo: str, programa: str, semestre: int, edad: int
    ) -> int:
        with self.bd.sesion() as c:
            cursor = c.execute(
                "INSERT INTO usuarios (nombre, correo, contrasena, tipo_usuario) VALUES (?, ?, ?, ?)",
                (nombre, correo, contrasena, TipoUsuario.ESTUDIANTE),
            )
            c.execute(
                "INSERT INTO estudiantes VALUES (?, ?, ?, ?, ?)",
                (cursor.lastrowid, codigo, programa, semestre, edad),
            )
            return cursor.lastrowid

    def crear_administrador(self, nombre: str, correo: str, contrasena: str, cargo: str) -> int:
        with self.bd.sesion() as c:
            cursor = c.execute(
                "INSERT INTO usuarios (nombre, correo, contrasena, tipo_usuario) VALUES (?, ?, ?, ?)",
                (nombre, correo, contrasena, TipoUsuario.ADMINISTRADOR),
            )
            c.execute("INSERT INTO administradores VALUES (?, ?)", (cursor.lastrowid, cargo))
            return cursor.lastrowid

    def actualizar(self, usuario: Usuario) -> None:
        with self.bd.sesion() as c:
            c.execute(
                "UPDATE usuarios SET nombre = ?, correo = ? WHERE id_usuario = ?",
                (usuario.nombre, usuario.correo, usuario.id_usuario),
            )
            match usuario:
                case Estudiante():
                    c.execute(
                        "UPDATE estudiantes SET programa_academico = ?, semestre = ?, edad = ? WHERE id_usuario = ?",
                        (usuario.programa_academico, usuario.semestre, usuario.edad, usuario.id_usuario),
                    )
                case Administrador():
                    c.execute(
                        "UPDATE administradores SET cargo = ? WHERE id_usuario = ?",
                        (usuario.cargo, usuario.id_usuario),
                    )

    def cambiar_contrasena(self, id_usuario: int, contrasena: str) -> None:
        with self.bd.sesion() as c:
            c.execute("UPDATE usuarios SET contrasena = ? WHERE id_usuario = ?", (contrasena, id_usuario))

    def listar(self) -> list[tuple[Usuario, datetime]]:
        with self.bd.sesion() as c:
            filas = c.execute(f"{self.CONSULTA} ORDER BY u.tipo_usuario, u.nombre").fetchall()
        return [(self._convertir(f), datetime.fromisoformat(f["creado_en"])) for f in filas]

    def eliminar(self, id_usuario: int) -> None:
        with self.bd.sesion() as c:
            c.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))

    def contar(self, tipo: TipoUsuario) -> int:
        with self.bd.sesion() as c:
            return c.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = ?", (tipo,)).fetchone()[0]


class RepositorioUnidades(Repositorio):
    def principal(self) -> UnidadAmigable:
        with self.bd.sesion() as c:
            fila = c.execute("SELECT * FROM unidades ORDER BY id_unidad LIMIT 1").fetchone()
        return UnidadAmigable(**dict(fila))

    def crear(self, nombre: str, ubicacion: str, contacto: str) -> int:
        with self.bd.sesion() as c:
            return c.execute(
                "INSERT INTO unidades (nombre, ubicacion, contacto) VALUES (?, ?, ?)", (nombre, ubicacion, contacto)
            ).lastrowid

    def actualizar(self, unidad: UnidadAmigable) -> None:
        with self.bd.sesion() as c:
            c.execute(
                "UPDATE unidades SET nombre = ?, ubicacion = ?, contacto = ? WHERE id_unidad = ?",
                (unidad.nombre, unidad.ubicacion, unidad.contacto, unidad.id_unidad),
            )

    def vacia(self) -> bool:
        with self.bd.sesion() as c:
            return c.execute("SELECT COUNT(*) FROM unidades").fetchone()[0] == 0


class RepositorioModulos(Repositorio):
    def listar(self) -> list[ModuloEducativo]:
        with self.bd.sesion() as c:
            filas = c.execute("SELECT * FROM modulos ORDER BY id_modulo").fetchall()
        return [ModuloEducativo(**dict(f)) for f in filas]

    def obtener(self, id_modulo: int) -> ModuloEducativo | None:
        with self.bd.sesion() as c:
            fila = c.execute("SELECT * FROM modulos WHERE id_modulo = ?", (id_modulo,)).fetchone()
        return ModuloEducativo(**dict(fila)) if fila else None

    def guardar(self, modulo: ModuloEducativo) -> int:
        valores = (modulo.titulo, modulo.tema, modulo.contenido, modulo.tipo_contenido)
        with self.bd.sesion() as c:
            if modulo.id_modulo is None:
                return c.execute(
                    "INSERT INTO modulos (titulo, tema, contenido, tipo_contenido) VALUES (?, ?, ?, ?)", valores
                ).lastrowid
            c.execute(
                "UPDATE modulos SET titulo = ?, tema = ?, contenido = ?, tipo_contenido = ? WHERE id_modulo = ?",
                (*valores, modulo.id_modulo),
            )
            return modulo.id_modulo

    def eliminar(self, id_modulo: int) -> None:
        with self.bd.sesion() as c:
            c.execute("DELETE FROM modulos WHERE id_modulo = ?", (id_modulo,))

    def preguntas(self, id_modulo: int) -> list[Pregunta]:
        with self.bd.sesion() as c:
            filas = c.execute(
                "SELECT * FROM preguntas WHERE id_modulo = ? ORDER BY id_pregunta", (id_modulo,)
            ).fetchall()
        return [
            Pregunta(f["id_pregunta"], f["id_modulo"], f["enunciado"], json.loads(f["opciones"]), f["respuesta"])
            for f in filas
        ]

    def agregar_pregunta(self, pregunta: Pregunta) -> None:
        with self.bd.sesion() as c:
            c.execute(
                "INSERT INTO preguntas (id_modulo, enunciado, opciones, respuesta) VALUES (?, ?, ?, ?)",
                (pregunta.id_modulo, pregunta.enunciado, json.dumps(pregunta.opciones, ensure_ascii=False),
                 pregunta.respuesta),
            )

    def con_preguntas(self) -> set[int]:
        with self.bd.sesion() as c:
            return {f[0] for f in c.execute("SELECT DISTINCT id_modulo FROM preguntas")}


class RepositorioEvaluaciones(Repositorio):
    @staticmethod
    def _convertir(fila: sqlite3.Row) -> Evaluacion:
        datos = dict(fila)
        datos["fecha"] = datetime.fromisoformat(datos["fecha"])
        return Evaluacion(**datos)

    def registrar(self, id_usuario: int, id_modulo: int, aciertos: int, total: int) -> Evaluacion:
        with self.bd.sesion() as c:
            id_evaluacion = c.execute(
                "INSERT INTO evaluaciones (id_usuario, id_modulo, aciertos, total) VALUES (?, ?, ?, ?)",
                (id_usuario, id_modulo, aciertos, total),
            ).lastrowid
            fila = c.execute("SELECT * FROM evaluaciones WHERE id_evaluacion = ?", (id_evaluacion,)).fetchone()
        return self._convertir(fila)

    def mejores(self, id_usuario: int) -> dict[int, Evaluacion]:
        with self.bd.sesion() as c:
            filas = c.execute(
                "SELECT * FROM evaluaciones WHERE id_usuario = ? ORDER BY aciertos * 1.0 / total, fecha",
                (id_usuario,),
            ).fetchall()
        return {f["id_modulo"]: self._convertir(f) for f in filas}

    def contar(self) -> int:
        with self.bd.sesion() as c:
            return c.execute("SELECT COUNT(*) FROM evaluaciones").fetchone()[0]

    def rendimiento_por_modulo(self) -> list[tuple[str, int, int]]:
        with self.bd.sesion() as c:
            filas = c.execute(
                """
                SELECT m.titulo, ROUND(AVG(e.aciertos * 100.0 / e.total)) AS promedio, COUNT(*) AS intentos
                FROM evaluaciones e JOIN modulos m ON m.id_modulo = e.id_modulo
                GROUP BY m.id_modulo ORDER BY promedio DESC
                """
            ).fetchall()
        return [(f["titulo"], int(f["promedio"]), f["intentos"]) for f in filas]


class RepositorioMetodos(Repositorio):
    @staticmethod
    def _convertir(fila: sqlite3.Row) -> MetodoAnticonceptivo:
        datos = dict(fila)
        datos["frecuencia"] = Frecuencia(datos["frecuencia"])
        for campo in ("hormonal", "con_estrogeno", "protege_its"):
            datos[campo] = bool(datos[campo])
        return MetodoAnticonceptivo(**datos)

    def listar(self) -> list[MetodoAnticonceptivo]:
        with self.bd.sesion() as c:
            filas = c.execute("SELECT * FROM metodos ORDER BY efectividad IS NULL, efectividad DESC, nombre").fetchall()
        return [self._convertir(f) for f in filas]

    def existe_nombre(self, nombre: str, excepto: int | None = None) -> bool:
        with self.bd.sesion() as c:
            fila = c.execute(
                "SELECT 1 FROM metodos WHERE nombre = ? AND id_metodo IS NOT ?", (nombre, excepto)
            ).fetchone()
        return fila is not None

    def guardar(self, metodo: MetodoAnticonceptivo) -> int:
        valores = (
            metodo.nombre, metodo.tipo, metodo.efectividad, metodo.frecuencia, metodo.descripcion,
            metodo.indicado_para, int(metodo.hormonal), int(metodo.con_estrogeno), int(metodo.protege_its),
        )
        with self.bd.sesion() as c:
            if metodo.id_metodo is None:
                return c.execute(
                    """
                    INSERT INTO metodos (nombre, tipo, efectividad, frecuencia, descripcion, indicado_para,
                                         hormonal, con_estrogeno, protege_its)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    valores,
                ).lastrowid
            c.execute(
                """
                UPDATE metodos SET nombre = ?, tipo = ?, efectividad = ?, frecuencia = ?, descripcion = ?,
                                   indicado_para = ?, hormonal = ?, con_estrogeno = ?, protege_its = ?
                WHERE id_metodo = ?
                """,
                (*valores, metodo.id_metodo),
            )
            return metodo.id_metodo

    def eliminar(self, id_metodo: int) -> None:
        with self.bd.sesion() as c:
            c.execute("DELETE FROM metodos WHERE id_metodo = ?", (id_metodo,))

    def vacio(self) -> bool:
        with self.bd.sesion() as c:
            return c.execute("SELECT COUNT(*) FROM metodos").fetchone()[0] == 0


class RepositorioCitas(Repositorio):
    CONSULTA = """
        SELECT c.*, u.nombre AS estudiante, COALESCE(e.codigo, '') AS codigo
        FROM citas c
        JOIN usuarios u ON u.id_usuario = c.id_usuario
        LEFT JOIN estudiantes e ON e.id_usuario = c.id_usuario
    """

    @staticmethod
    def _convertir(fila: sqlite3.Row) -> Cita:
        datos = dict(fila)
        datos["fecha"] = date.fromisoformat(datos["fecha"])
        datos["estado"] = EstadoCita(datos["estado"])
        return Cita(**datos)

    def obtener(self, id_cita: int) -> Cita | None:
        with self.bd.sesion() as c:
            fila = c.execute(f"{self.CONSULTA} WHERE c.id_cita = ?", (id_cita,)).fetchone()
        return self._convertir(fila) if fila else None

    def crear(self, id_usuario: int, id_unidad: int, fecha: date, hora: str, motivo: str) -> int:
        with self.bd.sesion() as c:
            return c.execute(
                "INSERT INTO citas (id_usuario, id_unidad, fecha, hora, estado, motivo) VALUES (?, ?, ?, ?, ?, ?)",
                (id_usuario, id_unidad, fecha.isoformat(), hora, EstadoCita.PENDIENTE, motivo),
            ).lastrowid

    def del_usuario(self, id_usuario: int) -> list[Cita]:
        with self.bd.sesion() as c:
            filas = c.execute(
                f"{self.CONSULTA} WHERE c.id_usuario = ? ORDER BY c.fecha DESC, c.hora DESC", (id_usuario,)
            ).fetchall()
        return [self._convertir(f) for f in filas]

    def listar(self, estado: EstadoCita | None = None) -> list[Cita]:
        filtro, parametros = ("WHERE c.estado = ?", (estado,)) if estado else ("", ())
        with self.bd.sesion() as c:
            filas = c.execute(f"{self.CONSULTA} {filtro} ORDER BY c.fecha, c.hora", parametros).fetchall()
        return [self._convertir(f) for f in filas]

    def horas_ocupadas(self, id_unidad: int, fecha: date) -> set[str]:
        with self.bd.sesion() as c:
            filas = c.execute(
                "SELECT hora FROM citas WHERE id_unidad = ? AND fecha = ? AND estado <> ?",
                (id_unidad, fecha.isoformat(), EstadoCita.CANCELADA),
            ).fetchall()
        return {f["hora"] for f in filas}

    def cambiar_estado(self, id_cita: int, estado: EstadoCita) -> None:
        with self.bd.sesion() as c:
            c.execute("UPDATE citas SET estado = ? WHERE id_cita = ?", (estado, id_cita))

    def reprogramar(self, id_cita: int, fecha: date, hora: str) -> None:
        with self.bd.sesion() as c:
            c.execute(
                "UPDATE citas SET fecha = ?, hora = ?, estado = ? WHERE id_cita = ?",
                (fecha.isoformat(), hora, EstadoCita.PENDIENTE, id_cita),
            )

    def contar(self, estado: EstadoCita) -> int:
        with self.bd.sesion() as c:
            return c.execute("SELECT COUNT(*) FROM citas WHERE estado = ?", (estado,)).fetchone()[0]


class RepositorioOrientaciones(Repositorio):
    @staticmethod
    def _convertir(fila: sqlite3.Row) -> Orientacion:
        return Orientacion(
            fila["id_orientacion"],
            fila["id_usuario"],
            datetime.fromisoformat(fila["fecha"]),
            json.loads(fila["recomendados"]),
        )

    def registrar(self, id_usuario: int, respuestas: dict, recomendados: list[str]) -> None:
        with self.bd.sesion() as c:
            c.execute(
                "INSERT INTO orientaciones (id_usuario, respuestas, recomendados) VALUES (?, ?, ?)",
                (id_usuario, json.dumps(respuestas, ensure_ascii=False),
                 json.dumps(recomendados, ensure_ascii=False)),
            )

    def del_usuario(self, id_usuario: int) -> list[Orientacion]:
        with self.bd.sesion() as c:
            filas = c.execute(
                "SELECT * FROM orientaciones WHERE id_usuario = ? ORDER BY fecha DESC, id_orientacion DESC",
                (id_usuario,),
            ).fetchall()
        return [self._convertir(f) for f in filas]

    def todas(self) -> list[Orientacion]:
        with self.bd.sesion() as c:
            return [self._convertir(f) for f in c.execute("SELECT * FROM orientaciones")]
