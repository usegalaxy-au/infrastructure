"""Slack notifications for the grouper Slack channel."""
import json

import slack

import config


class SlackNotifier:
    """Wraps slack.WebClient; suppresses sends during a dry run."""

    def __init__(self, token: str, dry_run: bool = True):
        self._client = slack.WebClient(token=token)
        self._dry_run = dry_run

    def notify(self, title: str, msg: str, colour: str) -> None:
        """Post a titled, coloured attachment to the log channel."""
        if not msg:
            return

        if self._dry_run:
            print(f"[dry run] Would notify Slack: {title}\n{msg}")
            return

        data = {
            'title': " ".join([title, config.SLACK_LOG_MENTIONS]),
            'color': colour,
            'text': msg,
        }
        self._client.chat_postMessage(
            channel=config.SLACK_LOG_CHANNEL,
            attachments=json.dumps([data]),
        )
