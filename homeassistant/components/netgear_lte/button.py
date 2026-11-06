"""Support for Netgear LTE buttons."""

from typing import override

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NetgearLTEConfigEntry
from .entity import LTEEntity

BUTTONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="reboot",
        translation_key="reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetgearLTEConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Netgear LTE buttons."""
    async_add_entities(
        NetgearLTEButton(entry, entity_description) for entity_description in BUTTONS
    )


class NetgearLTEButton(LTEEntity, ButtonEntity):
    """Netgear LTE button."""

    @override
    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.modem.router_restart()
