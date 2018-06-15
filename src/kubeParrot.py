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
MONITOR_NAMESPACES=[]
if 'MONITOR_NAMESPACES' in os.environ:
    MONITOR_NAMESPACES=os.environ['MONITOR_NAMESPACES'].split(",")


print "- Setup kubernetes client."
if 'USE_LOCAL_KUBECONFIG' in os.environ:
    config.load_kube_config()
else:
    config.load_incluster_config()
kube=client.CoreV1Api()
kubeAppApi=client.AppsV1Api()


print "- Setup Slack message Client."
if 'SLACK_WEBHOOK' in os.environ:
    SLACK_WEBHOOK=os.environ['SLACK_WEBHOOK']
slack = slackMessage(SLACK_WEBHOOK)


print "- Configuring Pod Monitor."
POD_INFO_LEVEL=3
if 'POD_INFO_LEVEL' in os.environ:
    POD_INFO_LEVEL=os.environ['POD_INFO_LEVEL']
configPodInformation={"level":POD_INFO_LEVEL,"namespaces": MONITOR_NAMESPACES}
pod=podInformation(kube,slack,configPodInformation)


print "- Configuring Deployment Monitor"
DEPLOY_INFO_LEVEL=3
if 'DEPLOY_INFO_LEVEL' in os.environ:
    DEPLOY_INFO_LEVEL=os.environ['DEPLOY_INFO_LEVEL']
configPodInformation={"level":DEPLOY_INFO_LEVEL,"namespaces": MONITOR_NAMESPACES}
deploy=deploymentInformation(kubeAppApi,slack,configPodInformation)


def main():
    print "- System started."
    while True:
        deploy.deployMonitor()
        pod.podMonitor()
        time.sleep(3)


if __name__ == '__main__':
    main()