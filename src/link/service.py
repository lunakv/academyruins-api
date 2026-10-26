from pydantic import HttpUrl, TypeAdapter, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.link.models import PendingRedirect, Redirect

_url_adapter = TypeAdapter(HttpUrl)


def is_valid_link(link: str) -> bool:
    """Whether the link is an absolute http(s) URL. Used for scraped links, which don't go through admin validation."""
    try:
        _url_adapter.validate_python(link)
        return True
    except ValidationError:
        return False


def get_redirect(db: Session, resource: str) -> str | None:
    stmt = select(Redirect.link).where(Redirect.resource == resource)
    return db.execute(stmt).scalar_one_or_none()


def get_pending_redirect(db: Session, resource: str) -> str | None:
    stmt = select(PendingRedirect.link).where(PendingRedirect.resource == resource)
    return db.execute(stmt).scalar_one_or_none()


def set_pending_redirect(db: Session, resource: str, link: str) -> None:
    pending: PendingRedirect | None = db.get(PendingRedirect, resource)
    if pending:
        pending.link = link
    else:
        db.add(PendingRedirect(resource=resource, link=link))
