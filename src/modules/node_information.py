import datetime

class node_information:
    lastInfo = {}
    count = 1

    def __init__(self,kubeClient,slackClient,config=None):
        self.kube = kubeClient
        self.slack = slackClient
        if not config:
            self.config = {"level":3}
        else:
            self.config = config


    def nodeMonitor(self):
        nodeList = self.kube.list_node().items
        for node in nodeList:
            healthInfo = self.checkHealth(node)
            if self.count > 1 and node.metadata.name not in self.lastInfo:
                self.log(3,"New Node in Kubernetes Cluster: "+node.metadata.name ,"good")
            self.lastInfo[node.metadata.name] = node
            self.lastInfo[node.metadata.name].healthInfo = healthInfo
        self.count+=1


    def checkHealth(self, nodeInfo):
        healthInfo = self.nodeHealthInfo(nodeInfo)
        nodeName = nodeInfo.metadata.name
        if nodeName in self.lastInfo:
            if healthInfo != self.lastInfo[nodeName].healthInfo:
                if healthInfo["problemsCount"] > 0:
                    list = [problem+"\n" for problem in healthInfo["problemsList"] ]
                    self.log(3,"Node "+nodeInfo.metadata.name+" with some problems:\n".join(list) ,"danger")
                else:
                    if healthInfo["schedulable"] != True:
                        self.log(3,"Node "+nodeInfo.metadata.name+" now is Unschedulable" ,"warning")
        return healthInfo


    def terminateCheck(self,nodeList):
        print ""

    def nodeHealthInfo(self,nodeInfo):
        readyStatus="None"
        kubelet="True"
        schedulable=True
        tags={"True": "Ready", "False": "Problem", "Unknown": "Unknown", "None":"None"}
        problems=[]
        goodStatus={"OutOfDisk": "False", 
                    "Ready": "True", 
                    "MemoryPressure": "False", 
                    "DiskPressure": "False",
                    "PIDPressure": "False",
                    "NetworkUnavailable": "False",
                    "ConfigOK": "True"
                    }
        for condition in nodeInfo.status.conditions:
            if condition.type in goodStatus:
                if condition.status != goodStatus.get(condition.type):
                    problems.append("%s: %s" % (condition.reason,condition.message))
            if condition.type == "Ready":
                kubelet=tags.get(condition.status)
                readyStatus=tags.get(condition.status)
        if len(problems) > 0:
            readyStatus+=",Problem"
        if nodeInfo.spec.unschedulable:
            readyStatus+=",NoSchedulable"
            schedulable=False
        nodeStatus={
                "status": readyStatus,
                "problemsList": problems,
                "problemsCount": len(problems),
                "schedulable": schedulable,
                "kubelet": kubelet,
            }
        return nodeStatus


    def log(self,level,message,type="good"):
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print ("%s - %s" % (date, message))
        if level <= self.config["level"]:
            payload={
                "username": "kube-info",
                "attachments":[ {
                      "color":type,
                      "text":message,
                  } ]
            }
            self.slack.sendMessage(payload)