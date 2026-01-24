"""Dependency injection container configuration."""

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config.settings import settings
from app.adapters.sqla.repositories.users import SqlAlchemyUsersRepository
from app.adapters.sqla.repositories.readings import SqlAlchemyReadingsRepository
from app.adapters.sqla.repositories.activation import SqlAlchemyActivationRequestsRepository
from app.core.services.registration import RegistrationService
from app.core.services.authentication import AuthenticationService
from app.core.services.reading_service import ReadingService
from app.core.services.activation import ActivationService


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Database engine
    engine = providers.Singleton(
        create_async_engine,
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True
    )

    # Session factory
    session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Repositories
    users_repo = providers.Factory(
        SqlAlchemyUsersRepository,
        session_factory=session_factory
    )

    readings_repo = providers.Factory(
        SqlAlchemyReadingsRepository,
        session_factory=session_factory
    )

    activation_repo = providers.Factory(
        SqlAlchemyActivationRequestsRepository,
        session_factory=session_factory
    )

    # Services
    registration_service = providers.Factory(
        RegistrationService,
        users_repo=users_repo
    )

    authentication_service = providers.Factory(
        AuthenticationService,
        users_repo=users_repo
    )

    reading_service = providers.Factory(
        ReadingService,
        readings_repo=readings_repo
    )

    activation_service = providers.Factory(
        ActivationService,
        users_repo=users_repo,
        activation_requests_repo=activation_repo
    )

    async def shutdown_resources(self):
        """Shutdown database engine."""
        await self.engine().dispose()