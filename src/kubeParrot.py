#!/usr/bin/python
from kubernetes import client, config
import time
from datetime import datetime
import os
from modules.podInformation import podInformation
from modules.deploymentInformation import deploymentInformation
from modules.slackMessage import slackMessage


#
print datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#
if 'SLACK_WEBHOOK' in os.environ:
  SLACK_WEBHOOK=os.environ['SLACK_WEBHOOK']

#
POD_INFO_LEVEL=3
MONITOR_NAMESPACES=None
if 'POD_INFO_LEVEL' in os.environ:
  POD_INFO_LEVEL=os.environ['POD_INFO_LEVEL']
if 'MONITOR_NAMESPACES' in os.environ:
  MONITOR_NAMESPACES=os.environ['MONITOR_NAMESPACES'].split(",")


print "- Setup kubernetes client."
config.load_incluster_config()
kube = client.CoreV1Api()
kubeAppApi = client.AppsV1Api()


print "- Setup Slack message Client."
slack = slackMessage(SLACK_WEBHOOK)

print "- Configuring Pod Monitor."
configPodInformation={"level":POD_INFO_LEVEL,"namespaces": MONITOR_NAMESPACES}
pod=podInformation(kube,slack,configPodInformation)

print "- Configuring Deployment Monitor"
deploy=deploymentInformation(kubeAppApi,slack)


print "- System started."
count=1
while True:
  pod.podMonitor()
  deploy.deployMonitor()
  count+=1
  time.sleep(3)
