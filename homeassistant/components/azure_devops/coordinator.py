"""Define the Azure DevOps DataUpdateCoordinator."""

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Final

from aioazuredevops.builds import DevOpsBuild
from aioazuredevops.client import DevOpsClient
from aioazuredevops.core import DevOpsProject
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ORG, DOMAIN
from .data import AzureDevOpsData

BUILDS_QUERY: Final = "?queryOrder=queueTimeDescending&maxBuildsPerDefinition=1"


def ado_exception_none_handler(func: Callable) -> Callable:
    """Handle exceptions or None to always return a value or raise."""

    async def handler(*args, **kwargs):
        try:
            response = await func(*args, **kwargs)
        except aiohttp.ClientError as exception:
            raise UpdateFailed from exception

        if response is None:
            raise UpdateFailed("No data returned from Azure DevOps")

        return response

    return handler


class AzureDevOpsDataUpdateCoordinator(DataUpdateCoordinator[AzureDevOpsData]):
    """Class to manage and fetch Azure DevOps data."""

    client: DevOpsClient
    organization: str
    project: DevOpsProject

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        entry: ConfigEntry,
    ) -> None:
        """Initialize global Azure DevOps data updater."""
        self.title = entry.title

        super().__init__(
            hass=hass,
            logger=logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=300),
        )

        self.client = DevOpsClient(session=async_get_clientsession(hass))
        self.organization = entry.data[CONF_ORG]

    @ado_exception_none_handler
    async def authorize(
        self,
        personal_access_token: str,
    ) -> bool:
        """Authorize with Azure DevOps."""
        await self.client.authorize(
            personal_access_token,
            self.organization,
        )
        if not self.client.authorized:
            raise ConfigEntryAuthFailed(
                "Could not authorize with Azure DevOps. You will need to update your"
                " token"
            )

        return True

    @ado_exception_none_handler
    async def get_project(
        self,
        project: str,
    ) -> DevOpsProject | None:
        """Get the project."""
        return await self.client.get_project(
            self.organization,
            project,
        )

    @ado_exception_none_handler
    async def _get_builds(self, project_name: str) -> list[DevOpsBuild] | None:
        """Get the builds."""
        return await self.client.get_builds(
            self.organization,
            project_name,
            BUILDS_QUERY,
        )

    async def _async_update_data(self) -> AzureDevOpsData:
        """Fetch data from Azure DevOps."""
        # Get the builds from the project
        builds = await self._get_builds(self.project.name)

        return AzureDevOpsData(
            organization=self.organization,
            project=self.project,
            builds=builds,
        )
