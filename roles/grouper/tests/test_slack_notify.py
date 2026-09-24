"""Tests for grouper.slack_notify.SlackNotifier."""
import logging
from unittest.mock import MagicMock

from grouper.slack_notify import SlackNotifier


def make_notifier(dry_run):
    notifier = SlackNotifier('fake-token', dry_run=dry_run)
    notifier._client = MagicMock()
    return notifier


def test_empty_message_is_not_posted():
    notifier = make_notifier(dry_run=False)

    notifier.notify('Title', '', 'good')

    notifier._client.chat_postMessage.assert_not_called()


def test_dry_run_does_not_post(caplog):
    caplog.set_level(logging.INFO)
    notifier = make_notifier(dry_run=True)

    notifier.notify('Title', 'some message', 'good')

    notifier._client.chat_postMessage.assert_not_called()
    assert 'Would notify Slack' in caplog.text


def test_commit_posts_with_title_and_colour():
    notifier = make_notifier(dry_run=False)

    notifier.notify('Title', 'some message', 'warning')

    notifier._client.chat_postMessage.assert_called_once()
    _, kwargs = notifier._client.chat_postMessage.call_args
    assert 'some message' in kwargs['attachments']
    assert 'warning' in kwargs['attachments']
