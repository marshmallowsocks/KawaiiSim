#############Safety pig!#########################						
#                            _ 					#
#	 _._ _..._ .-',     _.._(`))				#
#	'-. `     '  /-._.-'    ',/					#
#	   )         \            '. 				#
#	  / _    _    |             \ 				#
#	 |  a    a    /              | 				#
#	 \   .-.                     ;  			#
#	  '-('' ).-'       ,'       ; 				#
#	     '-;           |      .' 				#
#	        \           \    /	 				#
#	        | 7  .__  _.-\   \ 					#
#	        | |  |  ``/  /`  / 					#
#	       /,_|  |   /,_/   /					#
#	          /,_/      '`-'					#
#												#
#		  Oink Oink - Safety Pig 				#
#												#
# Safety pig keeps errors at bay. Long live SP! #
#################################################

from __future__ import division
from simpy import *
from simpy.util import start_delayed
from simpy.resources.container import ContainerGet
from simpy.resources.container import ContainerPut
from calendar import Calendar
import operator
import numpy as np

class ABC:

	_globalEnvironment = Environment()

	@classmethod
	def init(cls,calendar=Calendar(),numberOfUsers=1):

		ABC._globalEnvironment._now = 0.0

		simEntity._init(ABC._globalEnvironment)
		simEvent._init(ABC._globalEnvironment)
		ABC_core._init(calendar,numberOfUsers,ABC._globalEnvironment,CRR("Cloud Resource Registry 0"))
		
	@classmethod
	def startSimulation(cls,until=None):
		ABC_core._startSimulation(until)

	@classmethod
	def stopSimulation(cls):
		ABC_core._stopSimulation()
	
	@classmethod
	def create(cls):
		ABC_core._create()

class simEntity(Resource):
	"""Any runtime entity in our testbed is modelled as a simEntity. It serves as a base class for runtime entities. """
	
	types = {
			 -1:'simEntity',
			  0:'Cloud Resource Registry',
			  1:'Datacenter',
			  2:'Broker',
			  3:'Governor',
			  4:'VM',
			  5:'Host',
			  6:'Scheduler',
			  7:'Dispatcher'
			} 
			
	def __init__(self,name="",Type=-1,uid=-1):
 
 		if Type < 0 or Type >7 :
			raise ValueError("simEntity types can only be between 0-7,inclusive.")

		super(simEntity,self).__init__(simEntity._env)	

		self._id = hash(self)
		self._uid = uid
		self._name = name
		self._type = Type

		if self._type == 1 or self._type == 2:
			_notify(self)

	def __str__(self):
		details = ["ID:",str(self._id),"\n","Name:",self._name,"\n","Type:",simEntity.types[self._type]]
		return "".join(details)

	@classmethod
	def _init(cls,env):
		simEntity._env = env
	
	@property
	def uid(self):
	    return self._uid
	@uid.setter
	def uid(self, value):
	    self._uid = value
	
	@property
	def id(self):
	    return self._id

	@property
	def name(self):
		return self._name

	@property
	def entType(self):
	   	return simEntity.types[self._type]

	def log(self,*args,**kwargs):
		
		print str(args[0]).ljust(20),

		for message in args[1:]:
			print message,
		print	
	
	def _process(self,*args,**kwargs):
		"""Override the process method to implement custom behaviour."""
		pass

	def _update(self,*args,**kwargs):
		"""Override the update method in relevant classes."""
		pass

	def process(self):
		"""Exposed method for user defined behaviour"""
		pass

	def update(self):
		"""Exposed method for user defined behaviour"""
		pass

class simEvent(object):
	"""SimEvents model runtime processes in our testbed."""
	
	types = {
			 -1:'simEvent',
			  0:'Cloudlet'
			  } 

	def __init__(self,uid=-1,name="",Type=-1,entSrc=-1,entDest=-1):
 
		if Type < 0 or Type >1 :
			raise ValueError("simEvent types can only be between 0-1,inclusive.")

		self._id = hash(self)
		self._uid = uid
		self._name = name
		self._type = Type
		self._entSrc = entSrc
		self._entDest = entDest
		self._isActive = False
		self._isAlive = True
		
	def __str__(self):
		details = ["ID:",str(self._id),"\n","Name:",self._name,"\n","Type:",simEvent.types[self._type],"\n","Entity Source:",str(self._entSrc),"\n","Entity Destination:",str(self._entDest),"\n"]
		return "".join(details)

	@classmethod
	def _init(cls,env):
		simEvent._env = env

	@property
	def uid(self):
	    return self._uid
	@uid.setter
	def uid(self, value):
	    self._uid = value
	

	@property
	def id(self):
	    return self._id

	@property
	def name(self):
		return self._name

	@property
	def evType(self):
	   	return simEvent.types[self._type]
	
	@property
	def entSrc(self):
	    return self._entSrc

	@entSrc.setter
	def entSrc(self,src):
		self._entSrc = src
	
	@property
	def entDest(self):
	    return self._entDest
	
	@entDest.setter
	def entDest(self,dest):
		self._entDest = dest

	@property
	def isAlive(self):
	    return self._isAlive
	
	@property
	def isActive(self):
	    return self._isActive

	def getEnvironment(self):
		return simEvent._env

class Broker(simEntity):

	def __init__(self,uid=-1,name="",Type=2):

		super(Broker,self).__init__(name,Type,uid)
		
		self._vmList = []
		self._cloudletList = []
		self._submittedVMList = []
		self._submittedCloudletList = []
		self._recievedCloudletList = []
		self._recievedVmsList = []
		self._vmToDatacenterMap = {}
		self._coreEnvironment = ABC_core._env
		self._generator = False
		self._generated = -1
		self._userCost = 0
			
	@property
	def userCost(self):
	    return self._userCost
	
	@userCost.setter
	def userCost(self,value):
		self._userCost = value

	def addCloudletList(self,cloudletList):
		
		self._cloudletList = cloudletList
		for cloudlet in self._cloudletList:
			cloudlet.entSrc = self._id
	
	def addVMList(self,vmList):
		
		self._vmList = vmList
		for vm in self._vmList:
			vm._brokerId = self._id
	
	def logCost(self):
		self.log("Broker "+str(self.uid)+"<"+str(self.id)+"> cost:",self.userCost)

	def _getUserCloudlet(self,cloudlet):

		if len(self._submittedVMList) == 0:
			pass
		else:
			print "Yo"

			self._generated += 1
			i = self._generated
			i %= len(self._submittedVMList)
			
			print "yo"

			cloudlet.vmID = self._submittedVMList[i].id
			
			for vm in self._submittedVMList:

				if vm.id == cloudlet.vmID:
					cloudlet._vm = vm
				
				cloudlet.entDest = cloudlet.vmID
				ABC_core._CRR._getEntity(self._vmToDatacenterMap[cloudlet.vmID])._addCloudletToList(cloudlet) 
				self._submittedCloudletList.append(cloudlet)

	def process(self):

		"""Simple Allocation Test
		   VMs:For each datacenter, go through all VMs in the list, and try creating the VM in the datacenter. 
		   If created, remove VM from list, else, keep VM in list and try for next datacenter. All created 
		   VM ids are used as keys to point to their respective Datacenters in a dictionary. 

		   Cloudlets:Check if the cloudlet is bound. If bound, then submit the cloudlet to the datacenter by performing 
		   a lookup on the vm->datacenter map. If unbound, submit to the vms in round robin manner.
		   If the bound cloudlets VM could not be created, the cloudlet is assigned by round robin."""

		self.log(simEntity._env.now,"| Created broker",self.name,"<",self.id,">")

		datacenterList = ABC_core._CRR._getDatacenterList()
		maxTime = 0
		
		#Try for all datacenters
		for datacenter in datacenterList:
			
			datacenter._makeTotals()
			isCreated = False
			
			#Create a dummy list to iterate over, so that the original list can be modified.
			dummyList = list(self._vmList)
			for vm in dummyList:
				
				#This step creates the map (on the first iteration of the outer loop) and updates it.
				#Update the map to point to the next datacenter.
				self._vmToDatacenterMap[vm.id] = datacenter.id

				#This check relies on whether the datacenter can provide a host with the 
				#required characteristics. If not,it returns false.
				isCreated = ABC_core._CRR._getEntity(self._vmToDatacenterMap[vm.id])._addVMToList(vm) 
				
				#Successfully created, remove vm from waiting list.
				if isCreated is True:
					self._vmList.remove(vm)
					self.log(self._coreEnvironment.now,"| Created VM",vm.name,"<",vm.id,">",
						     "in host",vm.host.name,"<",vm.host.id,">")
					self._submittedVMList.append(vm)

			#Update the dummy list.
			dummyList = list(self._vmList)

		#At this point, any VMs left could not be created in any datacenter.
		if len(self._vmList) != 0:
			
			self.log(self._coreEnvironment.now,"| The following VMs could not be created:",[str(vm.name) for vm in self._vmList])
			#for vm in self._vmList:
			#	self.log(self._coreEnvironment.now,":",vm.name)

		#Done! All possible creations have been completed.
		#Now, need to get the cloudlets to the VMs
	
		if len(self._submittedVMList) == 0:
			self.log(self._coreEnvironment.now,"| No cloudlets created as no VMs exist.")

		elif self._generator is True:
			return 0.1

		else:
			dummyList = list(self._cloudletList)
			i = 0
			for cloudlet in dummyList:

				#If the cloudlet is unbound, bind it. 
				#Set entity destination, and send it to the appropriate datacenter.

				if cloudlet.vmID == -1 or cloudlet.vmID in [vm.id for vm in self._vmList]:
					
					cloudlet.vmID = self._submittedVMList[i].id
					i += 1
					i %= len(self._submittedVMList)

				for vm in self._submittedVMList:

					if vm.id == cloudlet.vmID:
						cloudlet._vm = vm
				
				cloudlet.entDest = cloudlet.vmID
				maxTime += cloudlet.cloudletLength/(cloudlet.vm.host.bw)
				ABC_core._CRR._getEntity(self._vmToDatacenterMap[cloudlet.vmID])._addCloudletToList(cloudlet) 
				self._submittedCloudletList.append(cloudlet)
				self._cloudletList.remove(cloudlet)

			#Done! All cloudlets have reached their datacenters. 
		return maxTime

	def _process(self):

		maxTime = self.process()

		#Timeout the environment with the totaltime taken to submit cloudlets.
		yield self._coreEnvironment.timeout(maxTime)
	#end of process method

	def _recieveCloudlet(self,cloudlet):
		
		if cloudlet not in self._recievedCloudletList:
			self._recievedCloudletList.append(cloudlet)

	def _recieveVM(self,vm):

		if vm not in self._recievedVmsList:
			self._recievedVmsList.append(vm)

	def getCloudlets(self):
		return self._submittedCloudletList

	def getRecievedCloudlets(self):
		return sorted(self._recievedCloudletList,key=lambda x:x.uid)

	def getRecievedVms(self):
		return sorted(self._recievedVmsList,key=lambda x:x.uid)

	def getCloudletData(self,sortby="uid"):

		print "*"*50,"Broker "+str(self.uid),"*"*54
		print "*"*50,"Cloudlet Data","*"*50
		print "_"*115
		print "Cloudlet ID".ljust(25),"VM ID".ljust(25),"Submission Time".ljust(25),"Start Time".ljust(25),"Finish Time".ljust(25)
		print "-"*115

		iterList = sorted(self._recievedCloudletList,key=operator.attrgetter(sortby))

		for cloudlet in iterList:
			print str(cloudlet.uid).ljust(25),str(cloudlet.vm.uid).ljust(25),str(cloudlet.submissionTime).ljust(25),
			print str(cloudlet.startTime[0]).ljust(25),str(cloudlet.clockState).ljust(25)
	
	def _get(self): #debugging method

		print "-----VMs-----"
		print self._vmList
		
		print "-----Cloudlets-----"
		print self._cloudletList
		
		print "-----Submitted VMs-----"
		print self._submittedVMList

		print "-----Submitted Cloudlets-----"
		print self._submittedCloudletList

		print "-----Map-----"
		print self._vmToDatacenterMap

		print "-----CRR-----"
		print ABC_core._CRR

class Cloudlet(simEvent):
	"""This class represents a task in ABC."""
	
	states = {
			  0:'Not started',
			  1:'Scheduled',
			  2:'Running',
			  3:'Paused',
			  4:'Stopped',
			  5:'Finished'
			  }

	def __init__(self,uid,name="",cloudletLength=-1,numberOfPes=-1,Type=1):
		
		super(Cloudlet,self).__init__(uid,name,Type)
		
		self._cloudletLength = cloudletLength
		self._numberOfPes = numberOfPes
		self._startTime = []
		self._processingTime = 0
		self._finishTime = -1
		self._remainingTime = -1
		self._submissionTime = 0
		self._vm = None
		self._vmID = -1 
		self._status = 0
		self._priority = 0

	@property
	def cloudletLength(self):
	    return self._cloudletLength
	@cloudletLength.setter
	def cloudletLength(self, value):
	    self._cloudletLength = value

	@property
	def startTime(self):
	    return self._startTime
	
	@property
	def waitingTime(self):
	    if self._status == 0: 
	    	return self._startTime - self._submissionTime 

	@property
	def priority(self):
	    return self._priority
	@priority.setter
	def priority(self, value):
	    self._priority = value
	
	@property
	def numberOfPes(self):
	    return self._numberOfPes
	@numberOfPes.setter
	def numberOfPes(self, value):
	    self._numberOfPes = value

	@property
	def status(self):
	    return Cloudlet.states[self._status]
	@status.setter
	def status(self, value):
	    if value > 5 or value < 0:
	    	raise ValueError("Cloudlet states can only be between 0-5,inclusive.")
	    self._status = value
	
	@property
	def userID(self):
	    return self._userID
	
	@property
	def submissionTime(self):
	    return self._submissionTime
	@submissionTime.setter
	def submissionTime(self, value):
	    
		if value < 100:
			self._submissionTime = 100
		
		else:
			self._submissionTime = value

	@property
	def processingTime(self):
	    return self._processingTime
	
	@property
	def vmID(self):
	    return self._vmID
	@vmID.setter
	def vmID(self, value):
	    self._vmID = value

	@property
	def vm(self):
	    return self._vm
	
	@property
	def clockState(self):
	    return self._finishTime
	
	def getData(self):

		print "ID:",self.uid 
		print "VM ID:",self._vm.id
		print "Submission time:",self._submissionTime
		print "Start time:",self._startTime
		print "Processing time:",self._processingTime
		print "Finish time:",self._finishTime

	def _process(self,vmEnvironment,processingTime=None):
		
		if processingTime is None:
			processingTime = self._processingTime
		
		yield ContainerGet(self.vm._pe,self._numberOfPes)
		self._startTime.append(vmEnvironment.now)
		
		if self.status is "Scheduled":
			self.vm.host.datacenter.datacenterManager._updateCloudlet(self,"started in VM",vmEnvironment.now)
			self.status = 2

		if self.status is "Paused":
			self.vm.host.datacenter.datacenterManager._updateCloudlet(self,"resumed in VM",vmEnvironment.now)
			self.status = 2
		 
		yield vmEnvironment.timeout(processingTime)		
		yield ContainerPut(self.vm._pe,self._numberOfPes)
		
		self._finishTime = vmEnvironment.now
		self._remainingTime -= processingTime
		
		if self._remainingTime != 0:
			self.vm.host.datacenter.datacenterManager._updateCloudlet(self,"paused in VM")
			self._processingTime += processingTime
			self.status = 3
		
		else:
			self.vm.host.datacenter.datacenterManager._updateCloudlet(self)
			
			if self.vm._CloudletScheduler._schedulerType == "CloudletTimeShared":
				self._processingTime += processingTime
			
			self.status = 5
		
		vmEnvironment.exit()
	
class ABC_core:
	"""The main simulation thread environment is initialized here. It also maintains useful characteristics."""
	"""ABC_core.init() *MUST* be called before any operations can be performed with this class."""
	
	@classmethod
	def _init(cls,calendar,numberOfUsers,env,CRR):
		
		print "Kawaiisim ver 1.0 alpha"
		print "Initializing simulation package.."
		print "Simulation package initialized."
		print "Time".ljust(20),
		print "| Message"
		print "-"*100
		ABC_core._env = env
		ABC_core._CRR = CRR
		ABC_core._DatacenterList = []
		ABC_core._BrokerList = []
		ABC_core._isActive = True
		ABC_core._calendar = calendar
		ABC_core.numberOfUsers = numberOfUsers

	@classmethod
	def _startSimulation(cls,until=None):
		
		"""First, creates all the necessary VMs in the datacenters. Then, submits cloudlets to datacenters,
		   accounting for overhead if needed.Finally,starts the environment run() method."""

		print str(ABC_core._env.now).ljust(20),"|","Starting simulation"

		for broker in sorted(ABC_core._BrokerList,key=lambda x:x.uid):
			ABC_core._env.process(broker._process())
		
		for datacenter in sorted(ABC_core._DatacenterList,key=lambda x:x.uid):
			ABC_core._env.process(datacenter._process(ABC_core._env))

		ABC_core._env.run(until=until)
		ABC_core._env._now = max([datacenter.clockState for datacenter in ABC_core._DatacenterList])

	@classmethod
	def _stopSimulation(cls):
		
		for datacenter in ABC_core._DatacenterList:
			datacenter.totalCost = datacenter.costPerUnit * datacenter.clockState

		for broker in ABC_core._BrokerList:
			for cloudlet in broker.getRecievedCloudlets():
				broker.userCost += cloudlet.vm.host.datacenter.costPerUnit * cloudlet.processingTime

		print str(ABC_core._env.now).ljust(20),"| No future events.."
		print str(ABC_core._env.now).ljust(20),"| Simulation shutting down now."
		
	@classmethod
	def _create(cls,entity):

		yield ABC_core.env.timeout(0.1)

def _notify(entity):

	if entity.entType == "Datacenter":
		ABC_core._DatacenterList.append(entity)
	
	if entity.entType == "Broker":
		ABC_core._BrokerList.append(entity)
	
	ABC_core._CRR._addEntity(entity)

class CRR(simEntity):

	def __init__(self,name="",Type=0):

		super(CRR,self).__init__(name,Type)
		
		self._DatacenterMap = {}
		self._BrokerMap = {}

	def __str__(self):

		print self._DatacenterMap.keys()
		print self._DatacenterMap.values()
		print self._BrokerMap.keys()
		print self._BrokerMap.values()
		return ""

	def _addEntity(self,entity):

		temp = {entity.id:entity}

		if entity.entType == "Datacenter":
			self._DatacenterMap[entity.id] = entity
			return True

		elif entity.entType == "Broker":
			self._BrokerMap[entity.id] = entity
			return True
	
		else:
			return False
	
	def _addEntityList(self,entityList):

		for entity in entityList:
			self.addEntity(entity)

	def _removeEntity(self,entityID):
		
		if entityID in self._BrokerMap:
			del self._BrokerMap[entityID]

		elif entityID in self._DatacenterMap:
			del self._DatacenterMap[entityID]

		else:
			return False

	def _getEntity(self,entityID):

		if entityID in self._BrokerMap:			
			return self._BrokerMap[entityID]

		elif entityID in self._DatacenterMap:
			return self._DatacenterMap[entityID]

		else:
			return False

	def _getDatacenterList(self):
		return self._DatacenterMap.values()

	def _getBrokerList(self):
		return self._BrokerMap.values()

class Governor(simEntity):

	def __init__(self,name="",Type=3):

		super(Governor,self).__init__(name,Type)
		
		self._vmList = []
		self._cloudletList = []
		self._hostList = []
		
		self._finishedHosts = {}
		self._finishedVms = {}
		self._finishedCloudlets = {}

	def _allocateVmToHost(self,host,vm):
		"""Method to allocate all VMs to hosts."""
		
		if host._VmScheduler._schedulerType is "VmSpaceShared":

			if vm._peAmount > host._peAmount:
				return False
			if vm._ramAmount > host._ramAmount:
				return False
			if vm._storageAmount > host._storageAmount:
				return False
			if vm._mipsAmount > host._mipsAmount:
				return False

			host._peAmount -= vm._peAmount
			host._ramAmount -= vm._ramAmount
			host._storageAmount -= vm._storageAmount
			host._mipsAmount -= vm._mipsAmount 
			vm.host = host
			host._addVm(vm)
			return True
		
		if host._VmScheduler._schedulerType is "VmTimeShared":

			if vm._peAmount > host._peAmount:
				return False
			if vm._ramAmount > host._ramAmount:
				return False
			if vm._storageAmount > host._storageAmount:
				return False
			if vm._mipsAmount > host._mipsAmount:
				return False

			host._storageAmount -= vm._storageAmount
			vm.host = host
			host._addVm(vm)
			return True
				
	def _scheduleVms(self):

		for host in self._hostList:

			host._VmScheduler._setParameters(host._vmList,simEntity._env)
			host._VmScheduler._process()

	def _scheduleCloudlets(self):

		for vm in self._vmList:

			vm._CloudletScheduler._setParameters(vm._cloudletList,simEntity._env)
			vm._CloudletScheduler._process()
	
	def _updateEntity(self,entity):
		"""Whenever an entity finishes, it notifies the Governor."""
		
		if entity.entType is "Host":
			self._finishedHosts[entity] = entity.clockState
		
		if entity.entType is "VM":
			self._finishedVms[entity] = entity.clockState
			broker = ABC_core._CRR._getEntity(entity._brokerId)
			broker._recieveVM(entity)

		self.log(entity.clockState,"|",entity.name,"<",entity.id,">","finished")

	def _updateCloudlet(self,cloudlet,message=None,time=None):
		
		if message is None:
			
			self._finishedCloudlets[cloudlet] = cloudlet.clockState
			self.log(cloudlet.clockState,"|",cloudlet.name,"<",cloudlet.id,">","finished in VM",cloudlet.vm.name,
				 	 "<",cloudlet.vm.id,">")
		
			broker = ABC_core._CRR._getEntity(cloudlet.entSrc)
			broker._recieveCloudlet(cloudlet)
			
		else:
			if time is None:
				self.log(cloudlet.clockState,"|",cloudlet.name,"<",cloudlet.id,">",message,cloudlet.vm.name,
					 	 "<",cloudlet.vm.id,">")
			else:
				self.log(time,"|",cloudlet.name,"<",cloudlet.id,">",message,cloudlet.vm.name,
					 	 "<",cloudlet.vm.id,">")
	
	def _dispatchCloudlet(self):
		
		for cloudlet in self._cloudletList:
			self.log(simEntity._env.now,"|","Sending",cloudlet.name,"<",cloudlet.id,
					 "> to VM",cloudlet.vm.name,"<",cloudlet.vm.id,">")
			cloudlet._remainingTime = cloudlet.cloudletLength/(cloudlet.numberOfPes*cloudlet.vm.mips)
			cloudlet.vm._addCloudletToList(cloudlet)

	def getFinishedVms(self):

		return sorted(self._finishedVms,key=lambda x:x.uid)

	def _update(self,vmList,cloudletList,hostList):

		self._vmList = vmList
		self._cloudletList = cloudletList
		self._hostList = hostList
		
class Datacenter(simEntity):

	def __init__(self,uid=-1,name="",hostList=[],costPerUnit=-1,Type=1):

		super(Datacenter,self).__init__(name,Type,uid)
		
		self._datacenterEnvironment = simEntity._env#Environment()

		self._datacenterManager = Governor()
		self._hostList = hostList
		self._totalMemory = -1
		self._totalCPU = -1
		self._totalBW = -1
		self._totalMIPS = -1
		self._totalStorage = -1
		self._maxMemory = -1
		self._maxBW = -1
		self._maxMIPS = -1
		self._maxCPU = -1
		self._maxStorage = -1 
		self._vmList = []
		self._cloudletList = []
		self._vmToHostMap = {}
		self._clockState = 0
		self._costPerUnit = costPerUnit
		self._totalCost = 0

		if len(self._hostList):

			for host in self._hostList:
				host._datacenter = self
				host._datacenterId = self._id

	@property
	def datacenterManager(self):
	    return self._datacenterManager

	@property
	def clockState(self):
	    return self._clockState
	
	@property
	def costPerUnit(self):
	    return self._costPerUnit

	@costPerUnit.setter
	def costPerUnit(self,value):
		self._costPerUnit = value

	@property
	def totalCost(self):
	    return self._totalCost

	@totalCost.setter
	def totalCost(self,value):
		self._totalCost = value

	def logCost(self):
		print "Datacenter "+str(self.uid)+"<"+str(self.id)+"> cost:",self.totalCost

	def addHost(self,host):

		self._hostList.append(host)
		host._datacenter = self 
		host._datacenterId = self._id

	def _setVMList(self,vmList):
		self._vmList = vmList

	def _addVMList(self,vmList):
		self._vmList += vmList

	def _addVMToList(self,vm):
		
		if self._canCreate(vm):
			return True

		return False

	def _addCloudletToList(self,cloudlet):
		self._cloudletList.append(cloudlet)

	def _setCloudletList(self,cloudletList):
		self._cloudletList = cloudletList	
			
	def _canCreate(self,vm):
		"""This method compares characteristics between the vm and the host. 
		   If compatible, the method returns true, and the vm is added to the 
		   datacenters internal list."""

		for host in self._hostList:

			if self._datacenterManager._allocateVmToHost(host,vm):
				self._vmList.append(vm)
				return True

		return False

	def _makeTotals(self):

		for host in self._hostList:

			self._totalCPU += host.pe
			self._totalMIPS += host.mips 
			self._totalMemory += host.ram
			self._totalBW += host.bw 
			self._totalStorage += host.storage

			if host.pe > self._maxCPU:
				self._maxCPU = host.pe
			if host.mips > self._maxMIPS:
				self._maxMIPS = host.mips
			if host.ram > self._maxMemory:
				self._maxMemory = host.ram
			if host.bw > self._maxBW:
				self._maxBW = host.bw
			if host.storage > self._maxStorage:
				self._maxStorage = host.storage

	def _process(self,coreEnvironment):
		"""This method is used to start the processing in the datacenter. First,
		   it updates the Governor with the new lists. Then, ... """
		
		if len(self._hostList) == 0:
			self.log(self._datacenterEnvironment.now,"| No hosts present in Datacenter. Aborting..")
		
		else:
			#Update the governor   
			self._datacenterManager._update(self._vmList,self._cloudletList,self._hostList)
			self._datacenterManager._dispatchCloudlet()
			self._datacenterManager._scheduleVms()
			self._datacenterManager._scheduleCloudlets()
					
			
			for host in self._hostList:
				self._datacenterEnvironment.process(host._process(self._datacenterEnvironment))

			self._datacenterEnvironment.run()
			self._clockState = max([host.clockState for host in self._hostList])
			self.log(self._clockState,"| Datacenter",self.name,
					 "<",self.id,">","has no future tasks.")
			yield coreEnvironment.timeout(0.1)

	
	def get(self): #debugging method

		print "-----Hosts-----"
		print self._hostList
		
		print "-----VMs-----"
		print self._vmList
		
		print "-----Cloudlets-----"
		print self._cloudletList
		#for i in self._cloudletList:
			#print i

class Host(simEntity):
	"""This class represents the physical hosts(bare-metal hypervisors)"""

	def __init__(self,uid=-1,name="",pe=0,mips=0,ram=0,bw=0,storage=0,VmScheduler=None,DatacenterID=-1,Type=5):

		super(Host,self).__init__(name,Type,uid)
		
		self._hostEnvironment = simEntity._env#Environment()

		self._pe = Container(self._hostEnvironment,pe,init=pe)
		self._mips = Container(self._hostEnvironment,mips,init=mips)
		self._ram = Container(self._hostEnvironment,ram,init=ram)
		self._bw = Container(self._hostEnvironment,bw,init=bw)
		self._storage = Container(self._hostEnvironment,storage,init=storage)
		self._peAmount = pe
		self._mipsAmount = mips
		self._storageAmount = storage
		self._ramAmount = ram
		self._bwAmount = bw
		self._datacenter = None
		self._DatacenterId = DatacenterID
		self._vmList = []
		self._isActive = False
		self._VmScheduler = VmScheduler
		self._clockState = 0
		
	@property
	def pe(self):
	    return self._peAmount
	@pe.setter
	def pe(self, value):
	    self._pe = Container(self._hostEnvironment,value)

	@property
	def mips(self):
	    return self._mipsAmount
	@mips.setter
	def mips(self, value):
	    self._pe = Container(self._hostEnvironment,value)

	@property
	def bw(self):
	    return self._bwAmount
	@bw.setter
	def bw(self, value):
	    self._bw = value

	@property
	def storage(self):
	    return self._storageAmount
	    
	@storage.setter
	def storage(self, value):
	    self._storage = Container(self._hostEnvironment,value)

	@property
	def ram(self):
	    return self._ramAmount
	@ram.setter
	def ram(self, value):
	    self._ram = Container(self._hostEnvironment,value)

	@property
	def DatacenterId(self):
	    return self._DatacenterId
	@DatacenterId.setter
	def DatacenterId(self, value):
	    self._DatacenterId = value

	@property
	def vmList(self):
	    return self._vmList
	
	@property
	def datacenter(self):
	    return self._datacenter
	@datacenter.setter
	def datacenter(self, value):
	    self._datacenter = value
	
	@property
	def clockState(self):
	    return self._clockState
	@clockState.setter
	def clockState(self, value):
	    self._clockState = value
	
	
	def _setVMList(self,vmList):
		self._vmList = vmList
	
	def _addVm(self,vm):
		self._vmList.append(vm)
		return True

	def _removeVm(self,vm):
		self._vmList.remove(vm)
		
	def get(self):

		print self.id,":",self._vmList
		print self._peAmount
		print self._ramAmount

		for vm in self._vmList:
			print vm.id,":",vm._clockState

	def _process(self,datacenterEnvironment):

		
		if len(self._vmList) == 0:
			yield datacenterEnvironment.timeout(0.1)

		else:
			
			self._hostEnvironment.run() 
			self.clockState = max([vm.clockState for vm in self._vmList])
			self.datacenter.datacenterManager._updateEntity(self)
			yield datacenterEnvironment.timeout(0.1)#self._clockState)
		
class Scheduler(simEntity):

	def __init__(self,name="",schedulerType="",Type=6):

		super(Scheduler,self).__init__(name,Type)
		self._schedulerType = schedulerType
		self._resourceList = []
		self._context = None	
	
	def _setParameters(self,resourceList,context):
		
		self._resourceList = resourceList
		self._context = context

	def vmSpaceShared(self):
		
		for vm in self._resourceList:
			self._context.process(vm._process(self._context))

	def vmTimeShared(self):
		
		totalMips = 0
		totalLen = 0
		
		for _ in xrange(self._resourceList[0].host.pe):
			totalMips += self._resourceList[0].host.mips
			
		for vm in self._resourceList:
			totalLen += vm.pe
					
		mipsShare = totalMips/totalLen

		for vm in self._resourceList:
			
			vm.mips = mipsShare*vm.pe
			self._context.process(vm._process(self._context))
	
	def cloudletSpaceShared(self):
		
		for cloudlet in self._resourceList:
				
			cloudlet._processingTime = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet.vm.mips) 
			cloudlet._remainingTime = cloudlet._processingTime

			if cloudlet.submissionTime == 0:
				self._context.process(cloudlet._process(self._context))
				cloudlet.status = 1
			else:
				start_delayed(self._context,cloudlet._process(self._context),cloudlet._submissionTime)
				cloudlet.status = 1
	def cloudletTimeShared(self):
		
		processTimes = {}
		resourceListStart = []
		resourceListDelayed = []
		
		for cloudlet in self._resourceList:		
			if cloudlet._submissionTime == 0:
				processTimes[cloudlet] = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
				cloudlet._remainingTime = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
				resourceListStart.append(cloudlet)
				cloudlet.status = 1
			else:
				resourceListDelayed.append(cloudlet)			
		
			time = 0
		
		while len(processTimes) == 0:
			time += 100

			dummyList = list(resourceListDelayed)

			for cloudlet in dummyList:
					if time >= cloudlet._submissionTime:
						processTimes[cloudlet] = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
						cloudlet._remainingTime = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
						resourceListDelayed.remove(cloudlet)
						cloudlet.status = 1
		
		while True:
			
			dummyList = list(resourceListDelayed)

			for cloudlet in dummyList:
					
				if time >= cloudlet._submissionTime:
					processTimes[cloudlet] = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
					cloudlet._remainingTime = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
					resourceListDelayed.remove(cloudlet)
			
			keys = processTimes.keys()
			
			for i in keys:
				
				dummyList = list(resourceListDelayed)

				for cloudlet in dummyList:
					
					if time >= cloudlet._submissionTime:
						processTimes[cloudlet] = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
						cloudlet._remainingTime = cloudlet._cloudletLength/(cloudlet._numberOfPes*cloudlet._vm.mips)
						resourceListDelayed.remove(cloudlet)

				if time == 0:
					self._context.process(i._process(self._context,100))
				else:
					start_delayed(self._context,i._process(self._context,100),time)
				
				processTimes[i] -= 100

				if processTimes[i] <= 0:
					del processTimes[i]
				
				time += 100
			
			if len(processTimes) == 0:
				if len(resourceListDelayed) == 0:
					break	
				else:
					time += 100
					
	types = {"VmSpaceShared":vmSpaceShared,
			 "VmTimeShared":vmTimeShared,
			 "CloudletSpaceShared":cloudletSpaceShared,
			 "CloudletTimeShared":cloudletTimeShared}

	def _process(self):
		Scheduler.types[self._schedulerType](self)

class VM(simEntity):
	"""This class represents VMs(application servers)"""
	
	def __init__(self,uid,name="",pe=0,mips=0,ram=0,bw=0,storage=0,CloudletScheduler=None,Host=None,Type=4):

		super(VM,self).__init__(name,Type,uid)

		self._vmEnvironment = simEntity._env#Environment()
		self._pe = Container(self._vmEnvironment,pe,init=pe)
		self._mips = Container(self._vmEnvironment,mips,init=mips)
		self._ram = Container(self._vmEnvironment,ram,init=ram)
		self._bw = Container(self._vmEnvironment,bw,init=bw)
		self._peAmount = pe
		self._mipsAmount = mips
		self._storageAmount = storage
		self._ramAmount = ram
		self._bwAmount = bw
		self._startup = 100
		self._storage = Container(self._vmEnvironment,ram)
		self._host = Host
		self._isActive = False
		self._cloudletList = []
		self._CloudletScheduler = CloudletScheduler
		self._clockState = 0
		self._brokerId = -1
		
	@property
	def pe(self):
		return self._peAmount
	@pe.setter
	def pe(self, value):
		self._pe = Container(self._vmEnvironment,value)
		self._peAmount = self._pe.capacity
	
	@property
	def mips(self):
		 return self._mipsAmount
	@mips.setter
	def mips(self, value):
		self._mips = Container(self._vmEnvironment,value)
		self._mipsAmount = self._mips.capacity

	@property
	def bw(self):
		return self._bwAmount
	@bw.setter
	def bw(self, value):
		self._bw = value
		self._bwAmount = self._bw.capacity

	@property
	def storage(self):
		return self._storageAmount
	@storage.setter
	def storage(self, value):
		self._storage = Container(self._vmEnvironment,value)
		self._storageAmount = self._storage.capacity
	
	@property
	def ram(self):
		return self._ramAmount
	@ram.setter
	def ram(self, value):
		self._ram = Container(self._vmEnvironment,value)
		self._ramAmount = self._ram.capacity

	@property
	def host(self):
		return self._host
	@host.setter
	def host(self, value):
		self._host = value

	@property
	def clockState(self):
	    return self._clockState
	@clockState.setter
	def clockState(self, value):
	    self._clockState = value
	
	def _addCloudletToList(self,cloudlet):
		
		self._cloudletList.append(cloudlet)

	def _process(self,hostEnvironment):
				
		if len(self._cloudletList) == 0:
			yield hostEnvironment.timeout(0.1)
		
		else:
			
			self.log(hostEnvironment.now,"| Starting VM",self.name,"<",self.id,">")
			yield hostEnvironment.timeout(self._startup)
			self.log(hostEnvironment.now,"| VM",self.name,"<",self.id,"> started")

			if self.host._VmScheduler._schedulerType is "VmSpaceShared":
				yield ContainerGet(self._host._pe,self._peAmount)
			
			yield ContainerGet(self._host._ram,self._ramAmount)
			yield ContainerGet(self._host._storage,self._storageAmount)

			self._vmEnvironment.run()	
			self.clockState = max([cloudlet.clockState for cloudlet in self._cloudletList])
			self.host.datacenter.datacenterManager._updateEntity(self)
			yield hostEnvironment.timeout(0.1)
			
			if self.host._VmScheduler._schedulerType is "VmSpaceShared":
				yield ContainerPut(self._host._pe,self._peAmount)
			
			yield ContainerPut(self._host._ram,self._ramAmount)
			yield ContainerPut(self._host._storage,self._storageAmount)

class CloudletGenerator(simEvent):
	"""A cloudlet generator class that runs a continuous simulation"""
	
	def __init__(self,uid,name="",cloudletLength=-1,numberOfPes=-1,broker=None,Type=1):

		super(CloudletGenerator,self).__init__(uid,name,Type)	

		self._generatedCloudlets = []
		self._cloudletLength = cloudletLength
		self._numberOfPes = numberOfPes
		self._broker = broker
		self._broker._generator = True
		simEvent._env.process(self.generate(simEvent._env))

	def generate(self,env):

		i = 0

		while True:
			
			cloudlet = self.spawnRandomProcess(i,self._name,self._type)	
			self._broker._getUserCloudlet(cloudlet)
			
			yield env.timeout(self._getNextArrivalTime(env))
			i += 1
			
			env.process(cloudlet._process(env))

	def spawnRandomProcess(self,uid,name,Type):
		return Cloudlet(uid,name,Type,self._cloudletLength,self._numberOfPes)

	def _getNextArrivalTime(self,env):
		return np.random.randint(env.now,env.now+1000,1)