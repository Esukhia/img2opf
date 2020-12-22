import os

import slack

client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])


def slack_notifier(message):
    response = client.chat_postMessage(channel="#ocr-logs", text=message)
