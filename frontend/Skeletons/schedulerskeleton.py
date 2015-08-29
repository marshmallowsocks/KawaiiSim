#Scheduler process skeleton

"""
The scheduler algorithm needs to be defined in a seperate method. After creating said algorithm method,
add the following definition:
Scheduler.types['<methodName>'] = <methodName>
This step is vital as the interal _process method looks up this dictionary to call the relevant scheduler 
algorithm. The schedulerType is now '<methodName>'.
"""

def <methodName>:

	"""
	Both vms and cloudlet scheduler algorithms rely on the process method. Use the following declaration
	to create a new process.
	
	self.spawnProcess(<entity>)
	
	If you need to spawn a delayed process, use the following declaration:
	
	self.spawnProcess(<entity>,<time>)
	
	Where <time> is the time you require the process to begin.
	You can use _resourceList to access the entities you are currently scheduling.
	You need not worry about resource acquisition within the scheduler; resource acquisition and withdrawal
	is handled internally and not part of the scheduler. The scheduler is merely responsible for arranging 
	the times at which the tasks are run. 

	If you are creating a cloudlet scheduling algorithm, you MUST also set the cloudlet's processing time.
	<cloudlet>.processingTime = <time>.
	An acceptable metric that is used extensively in this simulator is the ratio of the cloudlet length to 
	the vm mips rating. 
	"""

	pass