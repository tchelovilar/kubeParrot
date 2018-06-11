

class podInformation:
    newPods=[]

    def __init__(self,kubeClient,slackClient):
        self.lastInfo={}
        self.count=1
        self.kube=kubeClient
        self.slack=slackClient

    def podMonitor(self):
        listPods = self.kube.list_pod_for_all_namespaces(watch=False)
        self.podCheck(listPods)
        self.podTerminatedCheck()
        self.count+=1


    def podCheck(self,listPods):
        for pod in listPods.items:
            if pod.metadata.uid in self.lastInfo:
                #print "Encontrado no banco: "+pod.metadata.name
                if pod.status.phase != self.lastInfo[pod.metadata.uid].status.phase:
                    if pod.metadata.deletion_timestamp == None:
                        if (self.lastInfo[pod.metadata.uid].status.phase == "Pending"
                                and pod.status.phase == "Running"
                                and pod.metadata.uid in self.newPods
                            ):
                            print "Created Pod: "+pod.metadata.name
                            self.newPods.remove(pod.metadata.uid)
                        else:
                            print("Pod %s status changed from %s to %s" %
                                  (pod.metadata.name,
                                   self.lastInfo[pod.metadata.uid].status.phase,
                                   pod.status.phase)
                                 )
                    else:
                        print("Pod %s in termination process." % pod.metadata.name)
                    self.lastInfo[pod.metadata.uid]=pod
                    #print pod
                self.lastInfo[pod.metadata.uid].checkNumber=self.count
            else:
                self.lastInfo[pod.metadata.uid]=pod
                self.lastInfo[pod.metadata.uid].checkNumber=self.count
                if self.count > 1:
                    print "New pod found: "+pod.metadata.name
                    # Add new pods in list to validate after if this pod go out of Pending Status.
                    self.newPods.append(pod.metadata.uid)
                #print("%s\t%s\t%s" % (pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name))


    def podTerminatedCheck(self):
        lastCheckNumber=self.count-1
        terminatedPods=[]
        for pod in self.lastInfo:
            if self.lastInfo[pod].checkNumber == lastCheckNumber:
                print "Pod %s terminated." % self.lastInfo[pod].metadata.name
                terminatedPods.append(pod)
        for pod in terminatedPods:
            del self.lastInfo[pod]


    def containerCheck(self):
        print "temp"
