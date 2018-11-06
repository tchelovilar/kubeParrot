# About

This is a simple slack alert client for Kubernetes to send message in Slack Messenger
to notify about some changes in cluster.

## Features
 - Notify Pod changes: Create, Delete, Status Change and Restart
 - Notify Deploy changes: Create, Change


# Install

## Configure deployment
Use yaml files in deploy folder to deploy a Kubeparrot Pod for deploy, change
environment variables to setup to your linking.

| Variable           | Default Value | Example                   | Description |
| :---               | :---          | :---                      | :---        |
| *SLACK_WEBHOOK*    | Null          | http://slack.com/webhook  | Url for slack webhook |
| MONITOR_NAMESPACES | None          | production,default        | If you need monitor specific namespaces (comma separated). Default is all namespaces. |
| POD_INFO_LEVEL     | 3             | 3                         | Information Level. 1 - 4, greater is more detailed. |
| DEPLOY_INFO_LEVEL  | 3             | 3                         | Information Level. 1 - 4, greater is more detailed. |
| DEPLOY_INFO_LEVEL  |               |                           | Alpha Feature
| CHECK_INTERVAL     | 10            | 10                        | Define interval in seconds to verify changes on cluster. |

Apply config:

```
kubectl apply -f deploy/
```
