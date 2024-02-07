from sqlalchemy.orm import declarative_base

Base = declarative_base()


# noinspection PyUnresolvedReferences


def get_full_base():
    """Imports all database models before returning the Base object. Used for alembic migrations"""

    import src.cr.models  # noqa: F401
    import src.diffs.models  # noqa: F401
    import src.ipg.models  # noqa: F401
    import src.link.models  # noqa: F401
    import src.mtr.models  # noqa: F401

    return Base
