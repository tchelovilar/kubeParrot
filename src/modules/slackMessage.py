import json
import requests


class slackMessage:
    def __init__(self,webhookUrl):
        self.webhookUrl=webhookUrl
        # Set the webhook_url to the one provided by Slack when you create the webhook at https://my.slack.com/services/new/incoming-webhook/
        #webhook_url = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'

    def sendMessage(self,message):
        #slack_data = {'text': "Sup! We're hacking shit together @HackSussex :spaghetti:"}
        slack_data = {'text': "Sup! We're hacking shit together @HackSussex :spaghetti:"}
        # (text="Tako is a sushi", channel="#sushi", username="sushi-bot", icon_emoji=":sushi:"
        #https://api.slack.com/docs/message-formatting
        response = requests.post(
            webhook_url, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
        )
