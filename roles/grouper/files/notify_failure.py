#!/usr/bin/env python3
import sys

import slack

import config


def main():
    if len(sys.argv) != 2:
        print("Usage: notify_failure.py <message>", file=sys.stderr)
        sys.exit(1)

    message = sys.argv[1]
    client = slack.WebClient(token=config.SLACK_TOKEN)
    client.chat_postMessage(
        channel=config.SLACK_ALERT_CHANNEL,
        text=" ".join([message, config.SLACK_ALERT_MENTIONS]),
    )


if __name__ == "__main__":
    main()
