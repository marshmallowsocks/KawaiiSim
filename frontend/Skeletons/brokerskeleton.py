#Broker process skeleton

def process(self):

	"""
	Perform user actions here.For a broker, this involves:
	1) Create VMs in Datacenters
	2) Assign cloudlets to VMs
	You may use _vmList and _cloudletList to access the vms and cloudlets sent to the broker.
	"""

	self.log(simEntity._env.now,"| Created broker",self.name,"<",self.id,">")
	datacenterList = ABC_core._CRR._getResourceList() #Gets you the list of datacenters.
	timeout = 0.1 #default value, change as needed. Always >= 0.1.
	
	for datacenter in datacenterList:
		datacenter._makeTotals()

	"""
	Assign your vms to respective datacenters here. Steps involved:
	
	1) Check if the VM can be created in said Datacenter by invoking 
	   <datacenter>._addVMToList(<vm>) and catching its return value.
	
	2) If the VM was successfully created, update the internal map as such:
	   self._vmToDatacenterMap[<vm>.id] = <datacenter>.id	
	
	3) Remove the vm from the internal list and add it to the submitted list.
	   self._vmList.remove(<vm>)
	   self.log(self._coreEnvironment.now,"| Created VM",<vm>.name,"<",<vm>.id,">",
				"in host",<vm>.host.name,"<",<vm>.host.id,">")
	   self._submittedVMList.append(<vm>)
	
	Use your own logic with these statements.
	"""

	#Mandatory check for failed vms.
	if len(self._vmList) != 0:
		self.log(self._coreEnvironment.now,"| The following VMs could not be created:",
			[str(vm.name) for vm in self._vmList])
	
	#If no vms created, this simulation should exit.
	if len(self._submittedVMList) == 0:
			self.log(self._coreEnvironment.now,"| No cloudlets created as no VMs exist.")
	
	else:

	"""
	Assign your cloudlets to vms here. Steps involved:
	
	1) Check if the user has specifically bound the cloudlet or not. If unbound, set <cloudlet>.vmID,
	   and also set <cloudlet>._vm = <vm> , where <vm>.id == <cloudlet>.vmID. If bound, <cloudlet>.vmID
	   is already set, so just perform a sanity check and set <cloudlet>._vm 

	2) Once your cloudlet has a VM to go to, set its entity destination and add it to the vm:
		<cloudlet>.entDest = <cloudlet>.vmID
		ABC_core._CRR._getEntity(self._vmToDatacenterMap[<cloudlet>.vmID])._addCloudletToList(<cloudlet>) 
	
	3) Cleanup: Remove the cloudlet from the internal list and add it to the submitted list.	
		self._submittedCloudletList.append(<cloudlet>)
		self._cloudletList.remove(<cloudlet>)
	"""
	return timeout



	