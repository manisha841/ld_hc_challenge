import asyncio
import click
from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

alembic_cfg = Config("alembic.ini")


@click.group()
def cli():
    pass


@cli.command()
def init():
    """Initialize the database"""

    async def init_db():
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)
        await engine.dispose()

    asyncio.run(init_db())
    click.echo("Database initialized")


@cli.command()
def migrate():
    """Run database migrations"""
    command.upgrade(alembic_cfg, "head")
    click.echo("Migrations completed")


@cli.command()
def rollback():
    """Rollback the last migration"""
    command.downgrade(alembic_cfg, "-1")
    click.echo("Rollback completed")


@cli.command()
def create_migration():
    """Create a new migration"""
    message = click.prompt("Enter migration message")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    click.echo("Migration created")


if __name__ == "__main__":
    cli()
