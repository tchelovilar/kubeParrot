import json
import requests


class slackMessage:
    def __init__(self,webhookUrl):
        self.webhookUrl=webhookUrl

    def sendMessage(self,message):
        # (text="Tako is a sushi", channel="#sushi", username="sushi-bot", icon_emoji=":sushi:"
        # https://api.slack.com/docs/message-formatting
        response = requests.post(
            self.webhookUrl, data=json.dumps(message),
            headers={'Content-Type': 'application/json'}
        )
        #
        if response.status_code != 200:
            # raise ValueError(
            #     'Request to slack returned an error %s, the response is:\n%s'
            #     % (response.status_code, response.text)
            print ('Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
        )
