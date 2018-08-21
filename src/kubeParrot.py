#!/usr/bin/python
from kubernetes import client, config
import time
from datetime import datetime
import os
from modules.pod_information import pod_information
from modules.deployment_information import deployment_information
from modules.node_information import node_information
from modules.slack_message import slack_message


#
print "%s Starting..." % datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Global Options
MONITOR_NAMESPACES=[]
if 'MONITOR_NAMESPACES' in os.environ:
    MONITOR_NAMESPACES=os.environ['MONITOR_NAMESPACES'].split(",")
CHECK_INTERVAL=10
if 'CHECK_INTERVAL' in os.environ:
    CHECK_INTERVAL=os.environ['CHECK_INTERVAL']

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
    slack = slack_message(SLACK_WEBHOOK)
else:
    slack = None


print "- Configuring Pod Monitor."
POD_INFO_LEVEL=3
if 'POD_INFO_LEVEL' in os.environ:
    POD_INFO_LEVEL=os.environ['POD_INFO_LEVEL']
configPodInformation={"level":POD_INFO_LEVEL,"namespaces": MONITOR_NAMESPACES}
pod=pod_information(kube,slack,configPodInformation)


print "- Configuring Deployment Monitor"
DEPLOY_INFO_LEVEL=3
if 'DEPLOY_INFO_LEVEL' in os.environ:
    DEPLOY_INFO_LEVEL=os.environ['DEPLOY_INFO_LEVEL']
configPodInformation={"level":DEPLOY_INFO_LEVEL,"namespaces": MONITOR_NAMESPACES}
deploy=deployment_information(kubeAppApi,slack,configPodInformation)

print "- Configuring Node Monitor"
node=node_information(kube,slack)


def main():
    print "- System started."
    while True:
        deploy.deployMonitor()
        pod.podMonitor()
        node.nodeMonitor()
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()