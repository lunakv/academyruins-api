import os

import requests

from src.utils import logger

_uri = "https://api.pushover.net/1/messages.json"
_token = os.environ.get("PUSHOVER_APP_TOKEN")
_user = os.environ.get("PUSHOVER_USER_KEY")


def notify(message, title=None, uri=None, uri_title=None, formatted=None, log_level="debug"):
    if os.environ.get("USE_PUSHOVER") != "1":
        return
    payload = {"token": _token, "user": _user, "message": message}
    if title:
        payload["title"] = title
    if uri:
        payload["url"] = uri
    if uri_title:
        payload["url_title"] = uri_title
    if formatted:
        payload["html"] = 1

    requests.post(_uri, data=payload)
    logger.log(log_level, "Sending notification: %s", message)


def notify_scrape_error(message):
    notify(message, title="Scraping Error", log_level="error")


def _confirm_refresh_uri(doctype):
    return os.environ.get("BASE_URI", "") + f"/admin/update-link/{doctype}?token={os.environ.get('ADMIN_KEY')}"


def notify_new_cr(link):
    notify(
        formatted=True,
        message=f'New CR version is <a href="{link}">available</a> and ready to be parsed',
        title="Found new CR",
        uri=_confirm_refresh_uri("cr"),
        uri_title="Confirm Update",
    )


def notify_new_doc(link: str, name: str):
    notify(
        formatted=True,
        message=f'New {name.upper()} version is <a href="{link}">available</a>',
        title=f"Found new {name.upper()}",
        uri=_confirm_refresh_uri(name),
        uri_title="Confirm Update",
    )
