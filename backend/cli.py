"""CLI commands for managing the application."""

import asyncio
import click
from datetime import datetime, UTC
from uuid import uuid4

from app.container import Container
from app.core.models.user import User, UserRole
from app.adapters.sqla.mapping import bind_mappers
from app.core.services.registration import hash_password
from config.settings import settings


@click.group()
def cli():
    """СТ АВТО учет показаний эл. энергии CLI."""
    pass


@cli.command()
@click.option('--username', default=None, help='Username for the superuser (defaults to SUPERUSER_USERNAME from .env)')
@click.option('--email', default=None, help='Email for the superuser (defaults to SUPERUSER_EMAIL from .env)')
@click.option('--password', default=None, help='Password for the superuser (defaults to SUPERUSER_PASSWORD from .env)')
@click.option('--plot-number', default=None, help='Plot number for the superuser (defaults to SUPERUSER_PLOT_NUMBER from .env)')
def create_superuser(username: str | None, email: str | None, password: str | None, plot_number: str | None):
    """Create a superuser account with admin privileges and active status.

    You can provide credentials via:
    1. Command line options: --username, --email, --password, --plot-number
    2. Environment variables in .env: SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD, SUPERUSER_PLOT_NUMBER
    3. Interactive prompts (if not provided via options or .env)
    """

    # Get values from .env if not provided via command line
    username = username or settings.SUPERUSER_USERNAME
    email = email or settings.SUPERUSER_EMAIL
    password = password or settings.SUPERUSER_PASSWORD
    plot_number = plot_number or settings.SUPERUSER_PLOT_NUMBER

    # Prompt for missing values
    if not username:
        username = click.prompt('Username')
    if not email:
        email = click.prompt('Email')
    if not password:
        password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
    if not plot_number:
        plot_number = click.prompt('Plot number')

    async def _create_superuser():
        # Initialize mappers
        bind_mappers()

        # Initialize container
        container = Container()
        container.init_resources()

        try:
            users_repo = container.users_repo()

            # Check if username already exists
            existing_user = await users_repo.get_by_username(username)
            if existing_user:
                click.echo(f"Error: Username '{username}' already exists", err=True)
                return False

            # Check if plot number already exists
            existing_plot = await users_repo.get_by_plot_number(plot_number)
            if existing_plot:
                click.echo(f"Error: Plot number '{plot_number}' already exists", err=True)
                return False

            # Hash password
            password_hash = hash_password(password)

            # Create superuser
            superuser = User(
                id=uuid4(),
                plot_number=plot_number,
                username=username,
                email=email,
                password_hash=password_hash,
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.now(UTC),
                activated_at=datetime.now(UTC)
            )

            # Save to database
            await users_repo.add(superuser)

            click.echo(f"Superuser '{username}' created successfully!")
            click.echo(f"   Role: {superuser.role.value}")
            click.echo(f"   Active: {superuser.is_active}")
            click.echo(f"   Plot number: {plot_number}")

            return True

        except Exception as e:
            click.echo(f"Error creating superuser: {str(e)}", err=True)
            return False
        finally:
            # Dispose database engine
            engine = container.engine()
            await engine.dispose()

    # Run async function
    success = asyncio.run(_create_superuser())
    if not success:
        exit(1)


@cli.command()
def list_inactive_users():
    """List all inactive users waiting for activation."""

    async def _list_inactive_users():
        # Initialize mappers
        bind_mappers()

        # Initialize container
        container = Container()
        container.init_resources()

        try:
            users_repo = container.users_repo()
            inactive_users = await users_repo.get_inactive_users()

            if not inactive_users:
                click.echo("No inactive users found.")
                return

            click.echo(f"\nFound {len(inactive_users)} inactive user(s):\n")
            click.echo(f"{'Username':<20} {'Email':<30} {'Plot Number':<15} {'Created At':<20}")
            click.echo("-" * 85)

            for user in inactive_users:
                created = user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A'
                click.echo(f"{user.username:<20} {user.email:<30} {user.plot_number:<15} {created:<20}")

        except Exception as e:
            click.echo(f"Error listing users: {str(e)}", err=True)
        finally:
            # Dispose database engine
            engine = container.engine()
            await engine.dispose()

    asyncio.run(_list_inactive_users())


if __name__ == '__main__':
    cli()
