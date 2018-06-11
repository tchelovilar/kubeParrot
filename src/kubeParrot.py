#!/usr/bin/python
from kubernetes import client, config
import time
from modules.podInformation import podInformation
from modules.slackMessage import slackMessage


#
config.load_incluster_config()
kube = client.CoreV1Api()

#
slack = slackMessage("webhook")

#
pod=podInformation(kube,slack)

count=1
while True:
    pod.podMonitor()
    count+=1
    time.sleep(5)
