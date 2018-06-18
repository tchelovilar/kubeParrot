import datetime

class pod_information:
    newPods=[]
    podsWithProblem=[]

    def __init__(self,kubeClient,slackClient,config=None):
        self.lastInfo={}
        self.count=1
        self.kube=kubeClient
        self.slack=slackClient
        if not config:
            self.config={"level":3,"namespaces": []}
        else:
            self.config=config


    def podMonitor(self):
        listPods=[]
        if self.config["namespaces"]:
            for namespace in self.config["namespaces"]:
                listPods.extend(self.kube.list_namespaced_pod(namespace).items)
        else:
            listPods = self.kube.list_pod_for_all_namespaces(watch=False).items
        # Run checks
        self.containerCheck(listPods) # Conatiner Check need run before podCheck
        self.podCheck(listPods)
        

    def checkPodStatus(self,pod):
        if pod.status.container_statuses != None:
            for container in pod.status.container_statuses:
                if container.state.waiting.reason != None:
                    if container.state.waiting.reason != "ContainerCreating":
                        msg=("Pod *%s* have some problem:\n  Container *%s* with status *%s*:\n  %s" %
                            (pod.metadata.name,container.name,
                                container.state.waiting.reason,
                                container.state.waiting.message))
                        self.log(1,msg,"danger",pod.metadata.namespace)
                        self.podsWithProblem.append(pod.metadata.uid)
        if pod.status.conditions != None: 
            for condition in pod.status.conditions:
                if condition.reason not in [None,"ContainersNotReady"]:
                    msg=("Problem to start pod *%s*:\n  Reason: *%s*\n  %s" %
                          (pod.metadata.name,condition.reason,condition.message))
                    self.log(1,msg,"danger",pod.metadata.namespace)
                    self.podsWithProblem.append(pod.metadata.uid)
                    


    def podCheck(self,listPods):
        for pod in listPods:
            if pod.status.phase == "Pending" and pod.metadata.uid not in self.podsWithProblem:
                self.checkPodStatus(pod)
            if pod.status.phase == "Running" and pod.metadata.uid in self.podsWithProblem:
                self.podsWithProblem.remove(pod.metadata.uid)
            if pod.metadata.uid in self.lastInfo:
                if pod.status.phase != self.lastInfo[pod.metadata.uid].status.phase:
                    if pod.metadata.deletion_timestamp == None:
                        self.log(4,"Pod %s in termination process." % 
                                 pod.metadata.name,"good",pod.metadata.namespace)
            else:
                if self.count > 1:
                    self.log(3,"Pod has been created: "+pod.metadata.name,"good",pod.metadata.namespace)
            self.lastInfo[pod.metadata.uid]=pod
            self.lastInfo[pod.metadata.uid].checkNumber=self.count
        self.podTerminatedCheck()
        self.count+=1


    def podTerminatedCheck(self):
        lastCheckNumber=self.count-1
        terminatedPods=[]
        for pod in self.lastInfo:
            if self.lastInfo[pod].checkNumber == lastCheckNumber:
                self.log(3,"Pod has been deleted: %s" % 
                         self.lastInfo[pod].metadata.name,"danger",
                         self.lastInfo[pod].metadata.namespace)
                terminatedPods.append(pod)
        for pod in terminatedPods:
            del self.lastInfo[pod]


    def containerCheck(self,listPods):
        for pod in listPods:
            if pod.metadata.uid in self.lastInfo and isinstance(pod.status.container_statuses,list):
                lastInfoPod=self.lastInfo[pod.metadata.uid]
                i=0
                for container in pod.status.container_statuses:
                    if isinstance(lastInfoPod.status.container_statuses,list):
                        if container.restart_count > lastInfoPod.status.container_statuses[i].restart_count:
                            self.log(1,"Container *%s* from Pod *%s* has been restarted" % 
                                (container.name,pod.metadata.name),
                                "danger",pod.metadata.namespace )
                    i+=1


    def log(self,level,message,type="good",namespace=""):
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print ("%s Namespace: %s  Msg: %s" % (date, namespace, message))
        if level <= self.config["level"]:
            payload={
                "username": "kube-info",
                "attachments":[ {
                      "color":type,
                      "title":"Namespace: "+namespace,
                      "text":message,
                  } ]
            }
            self.slack.sendMessage(payload)
