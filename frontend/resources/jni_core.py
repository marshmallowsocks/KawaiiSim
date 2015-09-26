import os
os.environ['CLASSPATH'] = "/Users/vatsa/Documents/cloudsim-3.0.3/jars/cloudsim-3.0.3.jar"

from jnius import autoclass
from prettytable import PrettyTable
from collections import defaultdict
from itertools import groupby 

DecimalFormat = autoclass("java.text.DecimalFormat")
ArrayList = autoclass("java.util.ArrayList")
Calendar = autoclass("java.util.Calendar")
LinkedList = autoclass("java.util.LinkedList")
List = autoclass("java.util.List")

Cloudlet = autoclass("org.cloudbus.cloudsim.Cloudlet")
CloudletSchedulerTimeShared = autoclass("org.cloudbus.cloudsim.CloudletSchedulerTimeShared")
CloudletSchedulerSpaceShared = autoclass("org.cloudbus.cloudsim.CloudletSchedulerSpaceShared")
Datacenter = autoclass("org.cloudbus.cloudsim.Datacenter")
DatacenterBroker = autoclass("org.cloudbus.cloudsim.DatacenterBroker")
DatacenterCharacteristics = autoclass("org.cloudbus.cloudsim.DatacenterCharacteristics")
Host = autoclass("org.cloudbus.cloudsim.Host")
Pe = autoclass("org.cloudbus.cloudsim.Pe")
Storage = autoclass("org.cloudbus.cloudsim.Storage")
UtilizationModel = autoclass("org.cloudbus.cloudsim.UtilizationModel")
UtilizationModelFull = autoclass("org.cloudbus.cloudsim.UtilizationModelFull")
Vm = autoclass("org.cloudbus.cloudsim.Vm")
VmAllocationPolicySimple = autoclass("org.cloudbus.cloudsim.VmAllocationPolicySimple")
VmSchedulerTimeShared = autoclass("org.cloudbus.cloudsim.VmSchedulerTimeShared")
VmSchedulerSpaceShared = autoclass("org.cloudbus.cloudsim.VmSchedulerSpaceShared")
CloudSim = autoclass("org.cloudbus.cloudsim.core.CloudSim")
BwProvisionerSimple = autoclass("org.cloudbus.cloudsim.provisioners.BwProvisionerSimple")
PeProvisionerSimple = autoclass("org.cloudbus.cloudsim.provisioners.PeProvisionerSimple")
RamProvisionerSimple = autoclass("org.cloudbus.cloudsim.provisioners.RamProvisionerSimple")

def clean(string):

	return ''.join(string.split())

class SimulationSuite:

	def __init__(self,data):

		num_user = 1
		calendar = Calendar.getInstance()
		trace_flag = False

		CloudSim.init(num_user,calendar,trace_flag)

		hosts = [list(y) for x, y in groupby(data[0], lambda z: z == '\n') if not x]
		datacenters = [list(y) for x, y in groupby(data[1], lambda z: z == '\n') if not x]
		brokers = [list(y) for x, y in groupby(data[2], lambda z: z == '\n') if not x]
		vms = [list(y) for x, y in groupby(data[3], lambda z: z == '\n') if not x]
		cloudlets = [list(y) for x, y in groupby(data[4], lambda z: z == '\n') if not x]

		self.datacenterList = []
		self.brokerList = []

		self.hostToDatacenter = defaultdict(ArrayList)
		self.vmToBroker = defaultdict(ArrayList)
		self.cloudletToBroker = defaultdict(ArrayList)
		self.cloudletToVm = defaultdict(list)
		self.dataframe = {}
		
		self.hostIdToName = {}
		self.datacenterNameToId = {}
		self.brokerNameToId = {}
		self.vmIdToName = {}
		self.cloudletIdToName = {}
		self.brokerIdToUid = {}

		self.createHosts(hosts)
		self.createDatacenters(datacenters)
		self.createBrokers(brokers)
		self.createVms(vms)
		self.createCloudlets(cloudlets)
				
		for broker in self.brokerList:
			
			broker.submitVmList(self.vmToBroker[broker.getId()])
			broker.submitCloudletList(self.cloudletToBroker[broker.getId()])

		CloudSim.startSimulation()
		CloudSim.stopSimulation()

		self.dataframe["brokerList"] = self.brokerList
		self.dataframe["datacenterList"] = self.datacenterList
		self.dataframe["cloudletToVm"] = self.cloudletToVm
		
	def getDataframe(self):
		return self.dataframe

	def createHosts(self,hosts):
		
		for host in hosts:

			hostId = host[0].split(',')

			if len(hostId) == 1:
				
				peList = ArrayList()

				for pe in range(0,int(host[2])):
					peList.add(Pe(pe,PeProvisionerSimple(int(host[3]))))

				if host[7] == "Space Shared":
					scheduler = VmSchedulerSpaceShared(peList)
				else:
					scheduler = VmSchedulerTimeShared(peList)

				self.hostToDatacenter[int(host[8])].add(Host(int(host[0]),
														RamProvisionerSimple(int(host[4])),
														BwProvisionerSimple(int(host[6])),
														int(host[5]),
														peList,
														scheduler))

				self.hostIdToName[int(host[0])] = clean(host[1])
													   
			else:
				
				for Id in range(int(hostId[0]),int(hostId[1])+1):
					
					peList = ArrayList()

					for pe in range(0,int(host[2])):
						peList.add(Pe(pe,PeProvisionerSimple(int(host[3]))))

					if host[7] == "Space Shared":
						scheduler = VmSchedulerSpaceShared(peList)
					else:
						scheduler = VmSchedulerTimeShared(peList)

					self.hostToDatacenter[int(host[8])].add(Host(Id,
															RamProvisionerSimple(int(host[4])),
															BwProvisionerSimple(int(host[6])),
															int(host[5]),
															peList,
															scheduler))

					self.hostIdToName[Id] = clean(host[1])

	def createDatacenters(self,datacenters):

		arch = "x86"
		os = "Linux" 
		vmm = "Xen"
		time_zone = 10.0 
		storageList = LinkedList()
		
		for datacenter in datacenters:

			datacenterId = datacenter[0].split(',')

			if len(datacenterId) == 1:
				
				characteristics =  DatacenterCharacteristics(arch, 
												 os, 
												 vmm, 
												 self.hostToDatacenter[int(datacenter[0])], 
												 time_zone, 
												 float(datacenter[2]),
												 float(datacenter[2]),
												 float(datacenter[2]),
												 float(datacenter[2])
												 )

				self.datacenterList.append(Datacenter(clean(datacenter[1]),
												   	  characteristics,
												   	  VmAllocationPolicySimple(self.hostToDatacenter[int(datacenter[0])]),
												   	  storageList,0)
				)

				self.datacenterNameToId[datacenter[1]] = int(datacenter[0])
			
			else:
				
				for Id in range(int(datacenterId[0]),int(datacenterId[1])+1):
					
					characteristics =  DatacenterCharacteristics(arch, 
												 os, 
												 vmm, 
												 self.hostToDatacenter[Id], 
												 time_zone, 
												 float(datacenter[2]),
												 float(datacenter[2]),
												 float(datacenter[2]),
												 float(datacenter[2])
												 )

					self.datacenterList.append(Datacenter(clean(datacenter[1] + str(Id)),
												   		  characteristics,
												   		  VmAllocationPolicySimple(self.hostToDatacenter[Id]),
												   		  storageList,0)
					)

					self.datacenterNameToId[datacenter[1]] = Id
		
	def createBrokers(self,brokers):

		entity = None

		for broker in brokers:

			brokerId = broker[0].split(',')

			if len(brokerId) == 1:
				
				entity = DatacenterBroker(clean(broker[1]))
				self.brokerIdToUid[int(broker[0])] = entity.getId()
				self.brokerList.append(entity)
				self.brokerNameToId[broker[1]] = int(broker[0])
			
			else:
				for Id in range(int(brokerId[0]),int(brokerId[1])+1):
					
					entity = DatacenterBroker(clean(broker[1]+str(Id)))
					self.brokerIdToUid[int(broker[0])] = entity.getId()
					self.brokerList.append(DatacenterBroker(broker[1]+str(Id)))
					self.brokerNameToId[broker[1]] = Id
    
	def createVms(self,vms):

		for vm in vms:
			
			vmId = vm[0].split(',')

			if len(vmId) == 1:
				
				if vm[7] == "Space Shared":
					scheduler = CloudletSchedulerSpaceShared()
				else:
					scheduler = CloudletSchedulerTimeShared()
				
				temp = Vm(int(vm[0]),
						  self.brokerIdToUid[int(vm[8])],
						  int(vm[3]),
						  int(vm[2]),
						  int(vm[4]),
						  int(vm[6]),
						  int(vm[5]),
						  "Xen",
						  scheduler)
				
				self.vmToBroker[self.brokerIdToUid[int(vm[8])]].add(temp)
				self.vmIdToName[int(vm[8])] = clean(vm[1])
				
			else: 
				for Id in range(int(vmId[0]),int(vmId[1])+1):
					if vm[7] == "Space Shared":
						scheduler = CloudletSchedulerSpaceShared()
					else:
						scheduler = CloudletSchedulerTimeShared()

					temp = Vm(Id,
						      self.brokerIdToUid[int(vm[8])],
						  	  int(vm[3]),
						  	  int(vm[2]),
						  	  int(vm[4]),
						  	  int(vm[6]),
						  	  int(vm[5]),
						  	  "Xen",
						  	  scheduler)

					self.vmToBroker[self.brokerIdToUid[int(vm[8])]].add(temp)
					self.vmIdToName[Id] = clean(vm[1])
					
	def createCloudlets(self,cloudlets):

		fileSize = 300
		outputSize = 300
		utilizationModel = UtilizationModelFull()

		for cloudlet in cloudlets:
			
			cloudletId = cloudlet[0].split(',')

			if len(cloudletId) == 1:
				
				temp = Cloudlet(int(cloudlet[0]),
								int(cloudlet[2]),
								int(cloudlet[3]),
								fileSize,
								outputSize,
								utilizationModel,
								utilizationModel,
								utilizationModel)

				if cloudlet[6] != '':
					temp.setVmId(int(cloudlet[6]))

				temp.setUserId(self.brokerIdToUid[int(cloudlet[5])])
				
				self.cloudletToBroker[self.brokerIdToUid[int(cloudlet[5])]].add(temp)
				self.cloudletToVm[int(cloudlet[6])].append(int(cloudlet[0]))
				self.cloudletIdToName[int(cloudlet[0])] = clean(cloudlet[1])
			
			else:
				
				for Id in range(int(cloudletId[0]),int(cloudletId[1])+1):
					
					temp = Cloudlet(Id,
									int(cloudlet[2]),
									int(cloudlet[3]),
									fileSize,
									outputSize,
									utilizationModel,
									utilizationModel,
									utilizationModel)

					if cloudlet[6] != '':
						temp.setVmId(int(cloudlet[6]))

					temp.setUserId(self.brokerIdToUid[int(cloudlet[5])])

					self.cloudletToBroker[self.brokerIdToUid[int(cloudlet[5])]].add(temp)
					self.cloudletToVm[int(cloudlet[6])].append(Id)
					self.cloudletIdToName[Id] = clean(cloudlet[1])
					
	
					   


