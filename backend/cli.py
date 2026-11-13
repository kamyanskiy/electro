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


# Демо-садоводы: (username, plot_number, is_active)
DEMO_USERS = [
    ("ivanov", "12", True),
    ("petrova", "15", True),
    ("sidorov", "23", True),
    ("kuznetsova", "31", True),
    ("smirnov", "44", True),
    ("volkova", "58", True),
    ("morozov", "67", False),
    ("lebedeva", "72", False),
]


@cli.command()
@click.option('--password', default='demo12345', show_default=True, help='Password for all demo users')
@click.option('--months', default=12, show_default=True, help='How many months of readings to generate')
def seed_demo(password: str, months: int):
    """Seed demo users with monthly meter readings (for local development).

    Active users get one reading per month for the last N months, with
    cumulative day/night values growing month to month. Inactive users
    get no readings and show up as pending activation.
    Users that already exist are skipped, so the command is safe to re-run.
    """
    import random
    from datetime import date
    from decimal import Decimal
    from app.core.models.reading import Reading

    rng = random.Random(42)

    async def _seed_demo():
        bind_mappers()

        container = Container()
        container.init_resources()

        try:
            users_repo = container.users_repo()
            readings_repo = container.readings_repo()
            password_hash = hash_password(password)
            today = date.today()

            created_users = 0
            created_readings = 0

            for username, plot_number, is_active in DEMO_USERS:
                if await users_repo.get_by_username(username) or await users_repo.get_by_plot_number(plot_number):
                    click.echo(f"Skip '{username}': already exists")
                    continue

                now = datetime.now(UTC)
                user = User(
                    id=uuid4(),
                    plot_number=plot_number,
                    username=username,
                    email=f"{username}@example.com",
                    password_hash=password_hash,
                    role=UserRole.USER,
                    is_active=is_active,
                    created_at=now,
                    activated_at=now if is_active else None,
                )
                await users_repo.add(user)
                created_users += 1

                if not is_active:
                    continue

                # Накопительные показания счётчика: стартовое значение + месячный расход
                day_value = Decimal(rng.randint(1000, 9000))
                night_value = Decimal(rng.randint(500, 4000))
                for months_ago in range(months - 1, -1, -1):
                    year, month = today.year, today.month - months_ago
                    while month <= 0:
                        year, month = year - 1, month + 12
                    reading_day = min(rng.randint(18, 25), 28)
                    reading_date = date(year, month, reading_day)
                    if reading_date > today:
                        continue

                    # Зимой расход выше
                    winter = month in (11, 12, 1, 2, 3)
                    day_value += Decimal(rng.randint(250, 450) if winter else rng.randint(100, 250))
                    night_value += Decimal(rng.randint(120, 220) if winter else rng.randint(50, 120))

                    await readings_repo.add(Reading(
                        id=None,  # Will be set by database
                        user_id=user.id,
                        day_reading=day_value,
                        night_reading=night_value,
                        reading_date=reading_date,
                    ))
                    created_readings += 1

                click.echo(f"Created '{username}' (plot {plot_number}) with readings")

            click.echo(f"\nDone: {created_users} user(s), {created_readings} reading(s) created.")
            if created_users:
                click.echo(f"Demo users password: {password}")

        except Exception as e:
            click.echo(f"Error seeding demo data: {str(e)}", err=True)
        finally:
            engine = container.engine()
            await engine.dispose()

    asyncio.run(_seed_demo())


if __name__ == '__main__':
    cli()
