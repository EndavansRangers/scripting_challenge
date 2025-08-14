import os
import ssl
import smtplib
import mimetypes
from typing import Iterable, List, Tuple
from email.message import EmailMessage

class EmailConfigError(Exception):
    pass


# Cargar variables desde .env 
try:
    from dotenv import load_dotenv, find_dotenv
    _env_path = find_dotenv(usecwd=True)
    if _env_path:
        load_dotenv(_env_path, override=False)  # no pisa variables ya exportadas
except Exception:
    pass


def _load_smtp_config():
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    from_email = os.environ.get("FROM_EMAIL")

    if not (host and port and from_email):
        raise EmailConfigError("Faltan SMTP_HOST, SMTP_PORT o FROM_EMAIL en el entorno.")

    try:
        port = int(port)
    except ValueError:
        raise EmailConfigError("SMTP_PORT debe ser un entero.")

    return host, port, user, password, from_email

def _attach_files(msg: EmailMessage, attachments: List[Tuple[str, str]]):
    """
    attachments: lista de (filename, path)
    """
    for filename, path in attachments:
        # Detección de MIME
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=filename)

def send_email(subject: str, body: str, to: Iterable[str], attachments: List[Tuple[str, str]] = None):
    """
    Envía un email con asunto, cuerpo (texto plano) y adjuntos.
    Variables de entorno requeridas: SMTP_HOST, SMTP_PORT, FROM_EMAIL.
    Opcionales: SMTP_USER, SMTP_PASS (si el servidor requiere auth).
    """
    host, port, user, password, from_email = _load_smtp_config()

    # Normaliza destinatarios (limpia vacíos/None/espacios)
    to_list = [x.strip() for x in (to or []) if x and x.strip()]
    if not to_list:
        return  # sin destinatarios → nada que enviar

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_list)
    msg.set_content(body)

    if attachments:
        _attach_files(msg, attachments)

    context = ssl.create_default_context()

    # Conexión: SSL puro en 465, STARTTLS en 587, fallback si otro puerto
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            if user and password:
                server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            try:
                server.starttls(context=context)
                server.ehlo()
            except smtplib.SMTPException:
                # algunos servidores no requieren/soportan STARTTLS
                pass
            if user and password:
                server.login(user, password)
            server.send_message(msg)
