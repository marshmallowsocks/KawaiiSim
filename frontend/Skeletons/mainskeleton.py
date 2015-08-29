from core import *
from random import randint

def main():
	
	ABC.init() #Initialize the core package before starting the simulation.

	vmList = []
	cloudletList = [] 
	hostList = []
		
	# Use your own values here.
	hostPes = 8
	hostMIPS = 4000
	hostRam = 2048
	hostBw = 10000
	hostStorage = 100000

	for i in range(1):#use your own value 
		hostList.append(Host("Host "+str(i),hostPes,hostMIPS,hostRam,hostBw,hostStorage,Scheduler("Vm Scheduler","VmSpaceShared"))) 
		#OR:
		#hostList.append(Host("Host "+str(i),hostPes,hostMIPS,hostRam,hostBw,hostStorage,Scheduler("Vm Scheduler","VmTimeShared")))

	#Create datacenter object and pass hostList as a parameter to create hosts in datacenter.
	datacenter = Datacenter("Datacenter 0",hostList)
	#Create a new broker.
	broker = Broker("Broker 0")

	#Use your own values.
	vmPes = 2
	vmMIPS = 1000
	vmRam = 512
	vmBw = 1000
	vmStorage = 10000

	for i in range(2):
		vmList.append(VM("VM"+str(i),vmPes,vmMIPS,vmRam,vmBw,vmStorage,Scheduler("Cloudlet Scheduler","CloudletSpaceShared")))
	for i in range(2,4):
		vmList.append(VM("VM"+str(i),vmPes,vmMIPS,vmRam,vmBw,vmStorage,Scheduler("Cloudlet Scheduler","CloudletTimeShared")))
	 
	cloudletPes = 1
	cloudletSize = 400000
	cloudletRam = 512
	cloudletBw = 1000
	cloudletStorage = 1000
	
	for i in range(1,17):	
		cloudlet = Cloudlet(i,"Cloudlet "+str(i),cloudletSize,cloudletRam,cloudletPes,cloudletStorage,cloudletBw)
		cloudlet.submissionTime = randint(0,500)
		
		if i < 5: 
			cloudlet._vmID = vmList[0].id
		elif i < 9:
			cloudlet._vmID = vmList[1].id
		elif i < 13:
			cloudlet._vmID = vmList[2].id
		else:
			cloudlet._vmID = vmList[3].id
		
		cloudletList.append(cloudlet) 
			
	broker.addVMList(vmList)
	broker.addCloudletList(cloudletList)

	
	ABC.startSimulation()
	ABC.stopSimulation()
	
	broker.getCloudletData()
	

if __name__ == '__main__':
	main()