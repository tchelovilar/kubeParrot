import datetime

class deployment_information:
    config={}
    deployWithProblem=[]

    def __init__(self,kubeClient,slackClient,config=None):
        self.lastInfo={}
        self.count=1
        self.kube=kubeClient
        self.slack=slackClient
        if not config:
            self.config={"level":3,"namespaces": []}
        else:
            self.config=config

    def deployMonitor(self):
        listDeploys=[]
        if self.config["namespaces"]:
            for namespace in self.config["namespaces"]:
                listDeploys.extend(self.kube.list_namespaced_deployment(namespace).items)
        else:
            listDeploys = self.kube.list_deployment_for_all_namespaces().items
        self.checkContainers(listDeploys)
        self.updateLastInfo(listDeploys) # This need run at end


    def updateLastInfo(self,listDeploys):
        for deploy in listDeploys:
            if deploy.metadata.uid not in self.lastInfo and self.count > 1:
                self.newDeployCheck(deploy)
            self.checkAvailableReplicas(deploy) # This need run after checkContainer and newDeployCheck
            self.lastInfo[deploy.metadata.uid]=deploy
            self.lastInfo[deploy.metadata.uid].checkNumber=self.count
        self.count+=1

    def checkAvailableReplicas(self,deploy):
        if deploy.status.replicas != None:
            if (deploy.status.available_replicas < deploy.status.replicas and
                    deploy.metadata.uid not in self.deployWithProblem):
                msg=("Number of replicas for deployment *%s* is *%s* of *%s*" %
                    (deploy.metadata.name,
                    (0 if deploy.status.available_replicas is None else deploy.status.available_replicas),
                    deploy.status.replicas))
                self.log(2,msg, "danger", deploy.metadata.namespace)
                self.deployWithProblem.append(deploy.metadata.uid)
            if (deploy.metadata.uid in self.deployWithProblem and 
                    deploy.status.available_replicas == deploy.status.replicas):
                self.deployWithProblem.remove(deploy.metadata.uid)
                msg=("Number of replicas for deployment *%s* is *%s* of *%s*" %
                    (deploy.metadata.name,
                    (0 if deploy.status.available_replicas is None else deploy.status.available_replicas),
                    deploy.status.replicas))
                self.log(4,msg, "good", deploy.metadata.namespace)
                

    def newDeployCheck(self,deploy):
        self.log(2,"New Deployment Created: "+deploy.metadata.name, "good", 
                 deploy.metadata.namespace)
        # To avoid notification about available replicas.
        self.deployWithProblem.append(deploy.metadata.uid) 


    def checkContainers(self,listDeploys):
        for deploy in listDeploys:
            n=0
            if deploy.metadata.uid in self.lastInfo:
                msg=""
                for container in deploy.spec.template.spec.containers:
                    lastContainerInfo=self.lastInfo[deploy.metadata.uid].spec.template.spec.containers[n]
                    n+=1
                    if container != lastContainerInfo:
                        msg+="  Container *%s* changed:\n" % container.name
                    if container.image != lastContainerInfo.image:
                        msg+="  - New image: %s \n" % container.image
                if msg != "":
                    msg="Deployment *%s* has modified.\n%s" % (deploy.metadata.name,msg)
                    self.log(2,msg, "good", deploy.metadata.namespace)
                    # To avoid notification about available replicas.
                    self.deployWithProblem.append(deploy.metadata.uid) 


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
