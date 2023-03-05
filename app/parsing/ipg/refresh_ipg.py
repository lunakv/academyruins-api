from app.database import operations as ops
from app.database.db import SessionLocal
from app.database.models import Ipg
from app.parsing.utils.download_doc import download_doc


def refresh_ipg(link: str):
    _, name = download_doc(link, "ipg")
    with SessionLocal() as session:
        with session.begin():
            ops.upload_doc(session, name, Ipg)
