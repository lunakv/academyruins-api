from db import SessionLocal
from ipg.service import upload_ipg
from parsing.utils.download_doc import download_doc


def refresh_ipg(link: str):
    _, file_name = download_doc(link, "ipg")
    with SessionLocal() as session:
        with session.begin():
            upload_ipg(session, file_name)
