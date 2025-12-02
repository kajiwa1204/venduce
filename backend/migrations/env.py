import os
import sys
import logging

from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context

from app.db.database import DATABASE_URL
from app.db.base import target_metadata as Base


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your models so that 'target_metadata' is populated for autogenerate
# (this ensures Alembic sees the SQLAlchemy Table objects)
try:
    import app.models  # noqa: F401
except Exception:
    # If the import fails here, autogenerate will not work — let Alembic handle the error later
    pass


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


config.set_main_option("sqlalchemy.url", DATABASE_URL)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger(__name__)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# env.py expects `target_metadata` to be a MetaData object; we import it from app.db.base
target_metadata = Base

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Respect PGCLIENTENCODING (if set) by passing it as an option to libpq
    url = config.get_main_option("sqlalchemy.url")
    # If the URL contains an invalid client_encoding value (CP932), replace it with
    # the Postgres-acceptable name 'SJIS'. This can appear in DATABASE_URL query string.
    if url and "client_encoding=CP932" in url:
        logger.warning("Detected client_encoding=CP932 in sqlalchemy.url — replacing with SJIS")
        url = url.replace("client_encoding=CP932", "client_encoding=SJIS")
        config.set_main_option("sqlalchemy.url", url)
    pg_client_enc = os.getenv("PGCLIENTENCODING")
    connect_args = {}
    if pg_client_enc:
        # pass as libpq option: -c client_encoding=...
        connect_args["options"] = f"-c client_encoding={pg_client_enc}"
        # ensure the environment variable is visible to libpq/psycopg2
        os.environ["PGCLIENTENCODING"] = pg_client_enc

    # Try to create engine and connect. If psycopg2 raises a UnicodeDecodeError
    # while decoding server messages (common when server messages are in CP932/SJIS),
    # retry with CP932 client encoding forced.
    def _has_unicode_decode_error(exc: Exception) -> bool:
        # Walk the exception chain and detect a UnicodeDecodeError anywhere
        cur = exc
        while cur is not None:
            if isinstance(cur, UnicodeDecodeError):
                return True
            cur = getattr(cur, "__cause__", None) or getattr(cur, "__context__", None)
        return False

    try:
        logger.debug("Creating engine with connect_args=%s", {k: '***' if k == 'password' else v for k, v in connect_args.items()})
        connectable = create_engine(
            url,
            poolclass=pool.NullPool,
            connect_args=connect_args,
        )
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    except Exception as exc:  # catch broader exceptions to inspect nested Unicode errors
        if _has_unicode_decode_error(exc):
            logger.warning("UnicodeDecodeError detected during DB connect — will retry with CP932 client encoding")
            # log exception chain for diagnostics
            def _log_exc_chain(e: Exception) -> None:
                cur = e
                i = 0
                while cur is not None:
                    try:
                        logger.warning("exc[%d]: %s %r", i, type(cur), getattr(cur, "args", None))
                    except Exception:
                        logger.exception("failed to log exception[%d]", i)
                    cur = getattr(cur, "__cause__", None) or getattr(cur, "__context__", None)
                    i += 1

            _log_exc_chain(exc)

            # fallback: force SJIS (Postgres accepts 'SJIS' for Shift_JIS/CP932)
            # Note: 'CP932' is not a valid Postgres client_encoding value, which caused
            # the server-side error earlier. Use 'SJIS' which maps to the same byte encoding.
            fallback_args = dict(connect_args)
            fallback_args["options"] = "-c client_encoding=SJIS"
            os.environ["PGCLIENTENCODING"] = "SJIS"
            try:
                logger.debug("Attempting fallback connect with args=%s", {k: '***' if k == 'password' else v for k, v in fallback_args.items()})
                connectable = create_engine(url, poolclass=pool.NullPool, connect_args=fallback_args)
                with connectable.connect() as connection:
                    context.configure(connection=connection, target_metadata=target_metadata)

                    with context.begin_transaction():
                        context.run_migrations()
            except Exception as exc2:
                logger.error("Fallback connect also failed — dumping exception chain")
                _log_exc_chain(exc2)
                # Re-raise the original to preserve context
                raise
        else:
            # not a Unicode decode problem — re-raise so the caller sees the original traceback
            raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
