from pathlib import Path

from .base_datos import BaseDatos
from .datos_iniciales import poblar
from .repositorios import (
    RepositorioCitas,
    RepositorioEvaluaciones,
    RepositorioMetodos,
    RepositorioModulos,
    RepositorioOrientaciones,
    RepositorioUnidades,
    RepositorioUsuarios,
)
from .servicios import (
    ServicioCitas,
    ServicioContenido,
    ServicioCuentas,
    ServicioEvaluaciones,
    ServicioOrientacion,
    ServicioReportes,
)


class Sistema:
    def __init__(self, ruta: Path) -> None:
        bd = BaseDatos(ruta)
        bd.inicializar()

        usuarios = RepositorioUsuarios(bd)
        unidades = RepositorioUnidades(bd)
        modulos = RepositorioModulos(bd)
        metodos = RepositorioMetodos(bd)
        evaluaciones = RepositorioEvaluaciones(bd)
        citas = RepositorioCitas(bd)
        orientaciones = RepositorioOrientaciones(bd)

        poblar(usuarios, unidades, modulos, metodos)

        self.cuentas = ServicioCuentas(usuarios)
        self.contenido = ServicioContenido(modulos, metodos, unidades)
        self.evaluaciones = ServicioEvaluaciones(modulos, evaluaciones)
        self.citas = ServicioCitas(citas, unidades)
        self.orientacion = ServicioOrientacion(metodos, orientaciones)
        self.reportes = ServicioReportes(usuarios, citas, evaluaciones, orientaciones)
