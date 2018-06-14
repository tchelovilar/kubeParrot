import datetime

class podInformation:
    newPods=[]

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
        self.podTerminatedCheck()
        self.count+=1


    def podCheck(self,listPods):
        for pod in listPods:
            if pod.metadata.uid in self.lastInfo:
                if pod.status.phase != self.lastInfo[pod.metadata.uid].status.phase:
                    if pod.metadata.deletion_timestamp == None:
                        if (self.lastInfo[pod.metadata.uid].status.phase == "Pending"
                                and pod.status.phase == "Running"
                                and pod.metadata.uid in self.newPods
                              ):
                            self.log(3,"Created Pod: "+pod.metadata.name,"good",pod.metadata.namespace)
                            self.newPods.remove(pod.metadata.uid)
                        else:
                            msg=("Pod %s status changed from %s to %s" %
                                    (pod.metadata.name,
                                      self.lastInfo[pod.metadata.uid].status.phase,
                                      pod.status.phase ))
                            self.log(2,msg,"good",pod.metadata.namespace)
                    else:
                        self.log(4,"Pod %s in termination process." % pod.metadata.name,"good",pod.metadata.namespace)
                self.lastInfo[pod.metadata.uid]=pod
                #print pod
                self.lastInfo[pod.metadata.uid].checkNumber=self.count
            else:
                self.lastInfo[pod.metadata.uid]=pod
                self.lastInfo[pod.metadata.uid].checkNumber=self.count
                if self.count > 1:
                    if pod.status.phase == "Running":
                        self.log(3,"Pod has been created: "+pod.metadata.name,"good",pod.metadata.namespace)
                    else:
                        # Add new pods in list to validate after if this pod go out of
                        # Pending Status.
                        self.newPods.append(pod.metadata.uid)
                        self.log(4,"New pod found: "+pod.metadata.name,"good",pod.metadata.namespace)


    def podTerminatedCheck(self):
        lastCheckNumber=self.count-1
        terminatedPods=[]
        for pod in self.lastInfo:
            if self.lastInfo[pod].checkNumber == lastCheckNumber:
                self.log(3,"Pod has been deleted: %s" % self.lastInfo[pod].metadata.name,"danger",self.lastInfo[pod].metadata.namespace)
                terminatedPods.append(pod)
        for pod in terminatedPods:
            del self.lastInfo[pod]


    def containerCheck(self,listPods):
        for pod in listPods:
            if pod.metadata.uid in self.lastInfo:
                lastInfoPod=self.lastInfo[pod.metadata.uid]
                i=0
                for container in pod.status.container_statuses:
                    if isinstance(lastInfoPod.status.container_statuses,list):
                        if container.restart_count > lastInfoPod.status.container_statuses[i].restart_count:
                            self.log(1,"Container *%s* from Pod *%s* has been restarted" % (container.name,pod.metadata.name),
                                "danger",pod.metadata.namespace
                                )
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
