import hashlib
import hmac
import secrets

ALGORITMO = "sha256"
ITERACIONES = 210_000


def cifrar_contrasena(contrasena: str) -> str:
    sal = secrets.token_bytes(16)
    huella = hashlib.pbkdf2_hmac(ALGORITMO, contrasena.encode(), sal, ITERACIONES)
    return f"{ITERACIONES}${sal.hex()}${huella.hex()}"


def verificar_contrasena(contrasena: str, almacenada: str) -> bool:
    iteraciones, sal, huella = almacenada.split("$")
    calculada = hashlib.pbkdf2_hmac(ALGORITMO, contrasena.encode(), bytes.fromhex(sal), int(iteraciones))
    return hmac.compare_digest(calculada.hex(), huella)
