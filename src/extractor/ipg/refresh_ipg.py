from src.db import SessionLocal
from src.extractor.download_doc import download_doc
from src.ipg.service import upload_ipg


def refresh_ipg(link: str):
    _, file_name = download_doc(link, "ipg")
    with SessionLocal() as session:
        with session.begin():
            upload_ipg(session, file_name)
