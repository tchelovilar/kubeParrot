import datetime

class deploymentInformation:
  def __init__(self,kubeClient,slackClient,config=None):
    self.lastInfo={}
    self.count=1
    self.kube=kubeClient
    self.slack=slackClient
    if not config:
      self.config={"level":3,"namespaces": None}
    else:
      self.config=config

  def deployMonitor(self):
    listDeploys=[]
    if self.config["namespaces"]:
      for namespace in self.config["namespaces"]:
        listDeploys.extend(self.kube.list_namespaced_deployment(namespace).items)
    else:
      listDeploys = self.kube.list_deployment_for_all_namespaces().items
    self.checkList(listDeploys)


  def checkList(self,listDeploys):
    newDeploys=[]
    for deploy in listDeploys:
      if deploy.metadata.uid in self.lastInfo:
        self.lastInfo[deploy.metadata.uid].checkNumber=self.count
      else:
        self.lastInfo[deploy.metadata.uid]=deploy
        self.lastInfo[deploy.metadata.uid].checkNumber=self.count
        if self.count > 1:
          newDeploys.append(deploy.metadata.uid)
    self.newDeployCheck(newDeploys)
    self.count+=1


  def newDeployCheck(self,newDeploys):
    for deployID in newDeploys:
      self.log(2,"New Deployment Created: "+self.lastInfo[deployID].metadata.name, "good", self.lastInfo[deployID].metadata.namespace)


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
