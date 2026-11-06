"""Services tests for the Netgear LTE integration."""

from unittest.mock import patch

import pytest

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.components.netgear_lte.const import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from .conftest import HOST


async def test_set_option(hass: HomeAssistant, setup_integration: None) -> None:
    """Test service call set option."""
    with patch(
        "homeassistant.components.netgear_lte.eternalegypt.Modem.set_failover_mode"
    ) as mock_client:
        await hass.services.async_call(
            DOMAIN,
            "set_option",
            {CONF_HOST: HOST, "failover": "auto", "autoconnect": "home"},
            blocking=True,
        )
    assert len(mock_client.mock_calls) == 1

    with patch(
        "homeassistant.components.netgear_lte.eternalegypt.Modem.connect_lte"
    ) as mock_client:
        await hass.services.async_call(
            DOMAIN,
            "connect_lte",
            {CONF_HOST: HOST},
            blocking=True,
        )
    assert len(mock_client.mock_calls) == 1

    with patch(
        "homeassistant.components.netgear_lte.eternalegypt.Modem.disconnect_lte"
    ) as mock_client:
        await hass.services.async_call(
            DOMAIN,
            "disconnect_lte",
            {CONF_HOST: HOST},
            blocking=True,
        )
    assert len(mock_client.mock_calls) == 1

    with patch(
        "homeassistant.components.netgear_lte.eternalegypt.Modem.router_restart"
    ) as mock_client:
        await hass.services.async_call(
            DOMAIN,
            "reboot",
            {CONF_HOST: HOST},
            blocking=True,
        )
    assert len(mock_client.mock_calls) == 1

    with patch(
        "homeassistant.components.netgear_lte.eternalegypt.Modem.delete_sms"
    ) as mock_client:
        await hass.services.async_call(
            DOMAIN,
            "delete_sms",
            {CONF_HOST: HOST, "sms_id": 1},
            blocking=True,
        )
    assert len(mock_client.mock_calls) == 1

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "delete_sms",
            {CONF_HOST: "no-match", "sms_id": 1},
            blocking=True,
        )


async def test_press_reboot_button(
    hass: HomeAssistant,
    setup_integration: None,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test pressing reboot button restarts modem."""
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    reboot_button = next(
        entity_entry
        for entity_entry in er.async_entries_for_config_entry(
            entity_registry, entry.entry_id
        )
        if entity_entry.domain == BUTTON_DOMAIN
    )

    with patch(
        "homeassistant.components.netgear_lte.eternalegypt.Modem.router_restart"
    ) as mock_client:
        await hass.services.async_call(
            BUTTON_DOMAIN,
            SERVICE_PRESS,
            {ATTR_ENTITY_ID: reboot_button.entity_id},
            blocking=True,
        )
    assert len(mock_client.mock_calls) == 1
