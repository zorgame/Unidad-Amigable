class ErrorAplicacion(Exception):
    pass


class DatosInvalidos(ErrorAplicacion):
    pass


class CredencialesInvalidas(ErrorAplicacion):
    pass


class OperacionNoPermitida(ErrorAplicacion):
    pass
