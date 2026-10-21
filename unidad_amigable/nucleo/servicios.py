import re
import sqlite3
from collections import Counter
from dataclasses import asdict, replace
from datetime import date, datetime, timedelta

from .entidades import (
    MOTIVOS_CITA,
    TIPOS_CONTENIDO,
    TIPOS_METODO,
    Administrador,
    Cita,
    EstadoCita,
    Estudiante,
    Evaluacion,
    Frecuencia,
    MetodoAnticonceptivo,
    ModuloEducativo,
    Orientacion,
    PerfilOrientacion,
    Pregunta,
    Recomendacion,
    Resumen,
    TipoUsuario,
    UnidadAmigable,
    Usuario,
)
from .errores import CredencialesInvalidas, DatosInvalidos, OperacionNoPermitida
from .repositorios import (
    RepositorioCitas,
    RepositorioEvaluaciones,
    RepositorioMetodos,
    RepositorioModulos,
    RepositorioOrientaciones,
    RepositorioUnidades,
    RepositorioUsuarios,
)
from .seguridad import cifrar_contrasena, verificar_contrasena

PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
HORARIO = ("08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00")
DIAS_AGENDA = 21
LONGITUD_CONTRASENA = 8


def texto(valor: str | None, campo: str, minimo: int = 1) -> str:
    limpio = " ".join((valor or "").split())
    if len(limpio) < minimo:
        raise DatosInvalidos(f"El campo «{campo}» es obligatorio." if minimo == 1
                             else f"El campo «{campo}» debe tener al menos {minimo} caracteres.")
    return limpio


def bloque(valor: str | None, campo: str, minimo: int) -> str:
    limpio = (valor or "").strip()
    if len(limpio) < minimo:
        raise DatosInvalidos(f"El campo «{campo}» debe tener al menos {minimo} caracteres.")
    return limpio


def entero(valor: str | int | None, campo: str, minimo: int, maximo: int) -> int:
    try:
        numero = int(str(valor).strip())
    except ValueError:
        raise DatosInvalidos(f"El campo «{campo}» debe ser un número.") from None
    if not minimo <= numero <= maximo:
        raise DatosInvalidos(f"El campo «{campo}» debe estar entre {minimo} y {maximo}.")
    return numero


def decimal_opcional(valor: str | None, campo: str) -> float | None:
    limpio = (valor or "").strip().replace(",", ".")
    if not limpio:
        return None
    try:
        return float(limpio)
    except ValueError:
        raise DatosInvalidos(f"El campo «{campo}» debe ser un número.") from None


def correo_valido(valor: str | None) -> str:
    correo = (valor or "").strip().lower()
    if not PATRON_CORREO.match(correo):
        raise DatosInvalidos("Escribe un correo electrónico válido.")
    return correo


def contrasena_segura(valor: str | None) -> str:
    contrasena = valor or ""
    if len(contrasena) < LONGITUD_CONTRASENA or contrasena.isalpha() or contrasena.isdigit():
        raise DatosInvalidos(
            f"La contraseña debe tener mínimo {LONGITUD_CONTRASENA} caracteres y combinar letras con números."
        )
    return contrasena


def exigir_administrador(usuario: Usuario) -> None:
    if not usuario.es_administrador:
        raise OperacionNoPermitida("Esta acción solo está disponible para administradores.")


class ServicioCuentas:
    def __init__(self, usuarios: RepositorioUsuarios) -> None:
        self.usuarios = usuarios

    def iniciar_sesion(self, correo: str, contrasena: str) -> Usuario:
        registro = self.usuarios.credenciales((correo or "").strip().lower())
        if registro is None or not verificar_contrasena(contrasena or "", registro[1]):
            raise CredencialesInvalidas("Correo o contraseña incorrectos.")
        return self.usuarios.obtener(registro[0])

    def registrar_estudiante(
        self, nombre: str, correo: str, contrasena: str, codigo: str, programa: str, semestre: str, edad: str
    ) -> Estudiante:
        nombre = texto(nombre, "Nombre completo", 3)
        correo = correo_valido(correo)
        codigo = texto(codigo, "Código estudiantil", 4)
        programa = texto(programa, "Programa académico")
        semestre_valor = entero(semestre, "Semestre", 1, 12)
        edad_valor = entero(edad, "Edad", 14, 99)
        contrasena = contrasena_segura(contrasena)
        if self.usuarios.existe_correo(correo):
            raise DatosInvalidos("Ya existe una cuenta con ese correo.")
        if self.usuarios.existe_codigo(codigo):
            raise DatosInvalidos("Ese código estudiantil ya está registrado.")
        id_usuario = self.usuarios.crear_estudiante(
            nombre, correo, cifrar_contrasena(contrasena), codigo, programa, semestre_valor, edad_valor
        )
        return self.usuarios.obtener(id_usuario)

    def registrar_administrador(
        self, solicitante: Usuario, nombre: str, correo: str, contrasena: str, cargo: str
    ) -> Administrador:
        exigir_administrador(solicitante)
        nombre = texto(nombre, "Nombre completo", 3)
        correo = correo_valido(correo)
        cargo = texto(cargo, "Cargo")
        contrasena = contrasena_segura(contrasena)
        if self.usuarios.existe_correo(correo):
            raise DatosInvalidos("Ya existe una cuenta con ese correo.")
        return self.usuarios.obtener(
            self.usuarios.crear_administrador(nombre, correo, cifrar_contrasena(contrasena), cargo)
        )

    def actualizar_datos(self, usuario: Usuario, **cambios: str) -> Usuario:
        datos = {
            "nombre": texto(cambios.get("nombre"), "Nombre completo", 3),
            "correo": correo_valido(cambios.get("correo")),
        }
        if self.usuarios.existe_correo(datos["correo"], excepto=usuario.id_usuario):
            raise DatosInvalidos("Ese correo ya pertenece a otra cuenta.")
        match usuario:
            case Estudiante():
                datos["programa_academico"] = texto(cambios.get("programa_academico"), "Programa académico")
                datos["semestre"] = entero(cambios.get("semestre"), "Semestre", 1, 12)
                datos["edad"] = entero(cambios.get("edad"), "Edad", 14, 99)
            case Administrador():
                datos["cargo"] = texto(cambios.get("cargo"), "Cargo")
        actualizado = replace(usuario, **datos)
        self.usuarios.actualizar(actualizado)
        return actualizado

    def cambiar_contrasena(self, usuario: Usuario, actual: str, nueva: str, confirmacion: str) -> None:
        if not verificar_contrasena(actual or "", self.usuarios.contrasena(usuario.id_usuario)):
            raise CredencialesInvalidas("La contraseña actual no es correcta.")
        nueva = contrasena_segura(nueva)
        if nueva != confirmacion:
            raise DatosInvalidos("La confirmación no coincide con la nueva contraseña.")
        self.usuarios.cambiar_contrasena(usuario.id_usuario, cifrar_contrasena(nueva))

    def listar(self, solicitante: Usuario) -> list[tuple[Usuario, datetime]]:
        exigir_administrador(solicitante)
        return self.usuarios.listar()

    def eliminar(self, solicitante: Usuario, id_usuario: int) -> None:
        exigir_administrador(solicitante)
        if id_usuario == solicitante.id_usuario:
            raise OperacionNoPermitida("No puedes eliminar tu propia cuenta.")
        self.usuarios.eliminar(id_usuario)


class ServicioContenido:
    def __init__(self, modulos: RepositorioModulos, metodos: RepositorioMetodos, unidades: RepositorioUnidades) -> None:
        self.modulos = modulos
        self.metodos = metodos
        self.unidades = unidades

    def listar_modulos(self) -> list[ModuloEducativo]:
        return self.modulos.listar()

    def modulos_evaluables(self) -> set[int]:
        return self.modulos.con_preguntas()

    def guardar_modulo(
        self, solicitante: Usuario, id_modulo: int | None, titulo: str, tema: str, contenido: str, tipo: str
    ) -> int:
        exigir_administrador(solicitante)
        if tipo not in TIPOS_CONTENIDO:
            raise DatosInvalidos("Selecciona el tipo de contenido.")
        return self.modulos.guardar(
            ModuloEducativo(
                id_modulo,
                texto(titulo, "Título", 5),
                texto(tema, "Tema"),
                bloque(contenido, "Contenido", 20),
                tipo,
            )
        )

    def eliminar_modulo(self, solicitante: Usuario, id_modulo: int) -> None:
        exigir_administrador(solicitante)
        self.modulos.eliminar(id_modulo)

    def listar_metodos(self, tipo: str | None = None, busqueda: str = "") -> list[MetodoAnticonceptivo]:
        termino = busqueda.strip().lower()
        return [
            m for m in self.metodos.listar()
            if (tipo is None or m.tipo == tipo)
            and (not termino or termino in m.nombre.lower() or termino in m.descripcion.lower())
        ]

    def guardar_metodo(self, solicitante: Usuario, metodo: MetodoAnticonceptivo) -> int:
        exigir_administrador(solicitante)
        nombre = texto(metodo.nombre, "Nombre", 3)
        if metodo.tipo not in TIPOS_METODO:
            raise DatosInvalidos("Selecciona el tipo de método.")
        if metodo.frecuencia not in Frecuencia:
            raise DatosInvalidos("Selecciona la frecuencia de uso.")
        if metodo.efectividad is not None and not 0 < metodo.efectividad <= 100:
            raise DatosInvalidos("La efectividad debe estar entre 0 y 100.")
        if self.metodos.existe_nombre(nombre, excepto=metodo.id_metodo):
            raise DatosInvalidos("Ya existe un método con ese nombre.")
        return self.metodos.guardar(
            replace(
                metodo,
                nombre=nombre,
                frecuencia=Frecuencia(metodo.frecuencia),
                descripcion=texto(metodo.descripcion, "Descripción", 10),
                indicado_para=texto(metodo.indicado_para, "Indicado para", 5),
                con_estrogeno=metodo.hormonal and metodo.con_estrogeno,
            )
        )

    def eliminar_metodo(self, solicitante: Usuario, id_metodo: int) -> None:
        exigir_administrador(solicitante)
        self.metodos.eliminar(id_metodo)

    def unidad(self) -> UnidadAmigable:
        return self.unidades.principal()

    def actualizar_unidad(self, solicitante: Usuario, nombre: str, ubicacion: str, contacto: str) -> UnidadAmigable:
        exigir_administrador(solicitante)
        unidad = replace(
            self.unidades.principal(),
            nombre=texto(nombre, "Nombre", 5),
            ubicacion=texto(ubicacion, "Ubicación", 5),
            contacto=texto(contacto, "Contacto", 5),
        )
        self.unidades.actualizar(unidad)
        return unidad


class ServicioEvaluaciones:
    def __init__(self, modulos: RepositorioModulos, evaluaciones: RepositorioEvaluaciones) -> None:
        self.modulos = modulos
        self.evaluaciones = evaluaciones

    def preguntas(self, id_modulo: int) -> list[Pregunta]:
        return self.modulos.preguntas(id_modulo)

    def calificar(self, usuario: Usuario, id_modulo: int, respuestas: dict[int, int]) -> Evaluacion:
        preguntas = self.modulos.preguntas(id_modulo)
        if not preguntas:
            raise OperacionNoPermitida("Este módulo todavía no tiene evaluación.")
        pendientes = [p for p in preguntas if p.id_pregunta not in respuestas]
        if pendientes:
            raise DatosInvalidos(f"Te faltan {len(pendientes)} pregunta(s) por responder.")
        aciertos = sum(respuestas[p.id_pregunta] == p.respuesta for p in preguntas)
        return self.evaluaciones.registrar(usuario.id_usuario, id_modulo, aciertos, len(preguntas))

    def progreso(self, usuario: Usuario) -> dict[int, Evaluacion]:
        return self.evaluaciones.mejores(usuario.id_usuario)


class ServicioCitas:
    def __init__(self, citas: RepositorioCitas, unidades: RepositorioUnidades) -> None:
        self.citas = citas
        self.unidades = unidades

    @staticmethod
    def fechas_disponibles(hoy: date | None = None) -> list[date]:
        inicio = (hoy or date.today()) + timedelta(days=1)
        dias = (inicio + timedelta(days=n) for n in range(DIAS_AGENDA))
        return [d for d in dias if d.weekday() < 5]

    def horas_disponibles(self, fecha: date) -> list[str]:
        ocupadas = self.citas.horas_ocupadas(self.unidades.principal().id_unidad, fecha)
        return [h for h in HORARIO if h not in ocupadas]

    def _validar_franja(self, fecha: date | None, hora: str | None) -> None:
        if fecha not in self.fechas_disponibles():
            raise DatosInvalidos("Selecciona una fecha hábil disponible.")
        if hora not in self.horas_disponibles(fecha):
            raise DatosInvalidos("Esa hora ya no está disponible, elige otra.")

    def _propia(self, usuario: Usuario, id_cita: int) -> Cita:
        cita = self.citas.obtener(id_cita)
        if cita is None or (cita.id_usuario != usuario.id_usuario and not usuario.es_administrador):
            raise OperacionNoPermitida("La cita no existe.")
        if not cita.activa:
            raise OperacionNoPermitida(f"La cita ya está {cita.estado.lower()} y no se puede modificar.")
        return cita

    def agendar(self, estudiante: Usuario, fecha: date | None, hora: str | None, motivo: str | None) -> int:
        if estudiante.es_administrador:
            raise OperacionNoPermitida("Las citas se agendan desde una cuenta de estudiante.")
        if motivo not in MOTIVOS_CITA:
            raise DatosInvalidos("Selecciona el motivo de la cita.")
        if any(c.activa for c in self.citas.del_usuario(estudiante.id_usuario)):
            raise OperacionNoPermitida("Ya tienes una cita activa. Puedes reprogramarla o cancelarla.")
        self._validar_franja(fecha, hora)
        try:
            return self.citas.crear(estudiante.id_usuario, self.unidades.principal().id_unidad, fecha, hora, motivo)
        except sqlite3.IntegrityError:
            raise DatosInvalidos("Alguien acaba de tomar esa hora, elige otra.") from None

    def reprogramar(self, usuario: Usuario, id_cita: int, fecha: date | None, hora: str | None) -> None:
        self._propia(usuario, id_cita)
        self._validar_franja(fecha, hora)
        try:
            self.citas.reprogramar(id_cita, fecha, hora)
        except sqlite3.IntegrityError:
            raise DatosInvalidos("Alguien acaba de tomar esa hora, elige otra.") from None

    def cancelar(self, usuario: Usuario, id_cita: int) -> None:
        self._propia(usuario, id_cita)
        self.citas.cambiar_estado(id_cita, EstadoCita.CANCELADA)

    def cambiar_estado(self, solicitante: Usuario, id_cita: int, estado: EstadoCita) -> None:
        exigir_administrador(solicitante)
        self._propia(solicitante, id_cita)
        self.citas.cambiar_estado(id_cita, estado)

    def del_usuario(self, usuario: Usuario) -> list[Cita]:
        return self.citas.del_usuario(usuario.id_usuario)

    def proxima(self, usuario: Usuario) -> Cita | None:
        activas = [c for c in self.citas.del_usuario(usuario.id_usuario) if c.activa and c.fecha >= date.today()]
        return min(activas, key=lambda c: (c.fecha, c.hora), default=None)

    def listar(self, solicitante: Usuario, estado: EstadoCita | None = None) -> list[Cita]:
        exigir_administrador(solicitante)
        return self.citas.listar(estado)


class ServicioOrientacion:
    MAXIMO = 3

    def __init__(self, metodos: RepositorioMetodos, orientaciones: RepositorioOrientaciones) -> None:
        self.metodos = metodos
        self.orientaciones = orientaciones

    @staticmethod
    def _valorar(metodo: MetodoAnticonceptivo, perfil: PerfilOrientacion) -> Recomendacion | None:
        if metodo.tipo == "Emergencia" or metodo.efectividad is None:
            return None
        if perfil.restriccion_estrogeno and metodo.con_estrogeno:
            return None
        if perfil.acepta_hormonas == "no" and metodo.hormonal:
            return None

        recomendacion = Recomendacion(metodo, metodo.efectividad / 10)
        larga_duracion = metodo.frecuencia is Frecuencia.VARIOS_ANIOS

        if larga_duracion:
            recomendacion.motivos.append("No depende de recordarlo cada día y protege por años.")
            recomendacion.puntaje += {"largo": 3, "medio": 1.5, "corto": -1}[perfil.horizonte]
        if metodo.frecuencia is Frecuencia.DIARIA:
            if perfil.recuerda_diario:
                recomendacion.motivos.append("Encaja con tu facilidad para mantener una rutina diaria.")
            else:
                recomendacion.puntaje -= 4
        if metodo.frecuencia in (Frecuencia.MENSUAL, Frecuencia.TRIMESTRAL, Frecuencia.SEMANAL):
            recomendacion.puntaje += 1
            recomendacion.motivos.append(f"Requiere atención con frecuencia {metodo.frecuencia.lower()}, no a diario.")
        if metodo.protege_its:
            if perfil.pareja_estable:
                recomendacion.motivos.append("Protege frente a ITS; úsalo como respaldo.")
            else:
                recomendacion.puntaje += 4
                recomendacion.motivos.append("Es el único tipo de método que también protege frente a ITS.")
            if perfil.horizonte == "corto":
                recomendacion.puntaje += 1
        if not metodo.hormonal:
            recomendacion.motivos.append("No contiene hormonas.")
            if perfil.acepta_hormonas == "no":
                recomendacion.puntaje += 1
        recomendacion.motivos.append(f"Efectividad en uso típico: {metodo.efectividad:g} %.")
        return recomendacion

    def recomendar(self, usuario: Usuario, perfil: PerfilOrientacion) -> list[Recomendacion]:
        if perfil.horizonte not in ("corto", "medio", "largo") or perfil.acepta_hormonas not in ("si", "no", "nose"):
            raise DatosInvalidos("Responde todas las preguntas para recibir tu orientación.")
        valoradas = [r for m in self.metodos.listar() if (r := self._valorar(m, perfil))]
        valoradas.sort(key=lambda r: r.puntaje, reverse=True)
        seleccion: list[Recomendacion] = []
        for candidata in valoradas:
            if candidata.metodo.protege_its and any(r.metodo.protege_its for r in seleccion):
                continue
            seleccion.append(candidata)
            if len(seleccion) == self.MAXIMO:
                break
        if not perfil.pareja_estable and not any(r.metodo.protege_its for r in seleccion):
            barrera = next((r for r in valoradas if r.metodo.protege_its), None)
            if barrera:
                seleccion = [*seleccion[: self.MAXIMO - 1], barrera]
        self.orientaciones.registrar(usuario.id_usuario, asdict(perfil), [r.metodo.nombre for r in seleccion])
        return seleccion

    def historial(self, usuario: Usuario) -> list[Orientacion]:
        return self.orientaciones.del_usuario(usuario.id_usuario)


class ServicioReportes:
    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        citas: RepositorioCitas,
        evaluaciones: RepositorioEvaluaciones,
        orientaciones: RepositorioOrientaciones,
    ) -> None:
        self.usuarios = usuarios
        self.citas = citas
        self.evaluaciones = evaluaciones
        self.orientaciones = orientaciones

    def resumen(self, solicitante: Usuario) -> Resumen:
        exigir_administrador(solicitante)
        registros = self.orientaciones.todas()
        conteo = Counter(nombre for o in registros for nombre in o.recomendados)
        return Resumen(
            estudiantes=self.usuarios.contar(TipoUsuario.ESTUDIANTE),
            citas_pendientes=self.citas.contar(EstadoCita.PENDIENTE) + self.citas.contar(EstadoCita.CONFIRMADA),
            citas_atendidas=self.citas.contar(EstadoCita.ATENDIDA),
            evaluaciones=self.evaluaciones.contar(),
            orientaciones=len(registros),
            rendimiento_modulos=self.evaluaciones.rendimiento_por_modulo(),
            metodos_recomendados=conteo.most_common(5),
        )
