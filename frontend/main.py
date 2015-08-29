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

import os
import sys
from platform import system,version
from itertools import groupby
from collections import defaultdict
import cPickle as pickle
from PySide.QtCore import *
from PySide.QtGui import *
import matplotlib
import numpy as np
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from resources.ui import Ui_MainWindow
from resources.core import *

class NULL(QObject):

	text = Signal(str)

	def __init__(self):

		super(NULL,self).__init__()

	def write(self,text):
		pass

class RunBody(QObject):

	dataAcquired = Signal(dict)
	finished = Signal()

	def __init__(self,dataFile,randomGenerator,callback):
		
		super(RunBody,self).__init__()
		self.file = dataFile
		self.mode = randomGenerator
		self.dataAcquired.connect(callback)
		
	def run(self):

		ABC.init()

		with open(self.file,"r") as f:
			data = pickle.load(f)
			
		hosts = [list(y) for x, y in groupby(data[0], lambda z: z == '\n') if not x]
		datacenters = [list(y) for x, y in groupby(data[1], lambda z: z == '\n') if not x]
		brokers = [list(y) for x, y in groupby(data[2], lambda z: z == '\n') if not x]
		vms = [list(y) for x, y in groupby(data[3], lambda z: z == '\n') if not x]
		cloudlets = [list(y) for x, y in groupby(data[4], lambda z: z == '\n') if not x]
		
		datacenterList = []
		brokerList = []
		
		hostToDatacenter = defaultdict(list)
		vmToBroker = defaultdict(list)
		cloudletToBroker = defaultdict(list)
		cloudletToVm = {}
		dataframe = {}

		for host in hosts:
			
			hostId = host[0].split(',')

			if len(hostId) == 1:
				if host[7] == "Space Shared":
					hostToDatacenter[int(host[8])].append(Host(int(host[0]),host[1],int(host[2]),int(host[3]),int(host[4]),int(host[6]),int(host[5]),Scheduler("Vm Scheduler","VmSpaceShared")))
				else:
					hostToDatacenter[int(host[8])].append(Host(int(host[0]),host[1],int(host[2]),int(host[3]),int(host[4]),int(host[6]),int(host[5]),Scheduler("Vm Scheduler","VmTimeShared")))
			
			else:
				for Id in range(int(hostId[0]),int(hostId[1])+1):
					if host[7] == "Space Shared":
						hostToDatacenter[int(host[8])].append(Host(Id,host[1]+str(Id),int(host[2]),int(host[3]),int(host[4]),int(host[6]),int(host[5]),Scheduler("Vm Scheduler","VmSpaceShared")))
					else:
						hostToDatacenter[int(host[8])].append(Host(Id,host[1]+str(Id),int(host[2]),int(host[3]),int(host[4]),int(host[6]),int(host[5]),Scheduler("Vm Scheduler","VmTimeShared")))

		for datacenter in datacenters:

			datacenterId = datacenter[0].split(',')

			if len(datacenterId) == 1:
				datacenterList.append(Datacenter(int(datacenter[0]),datacenter[1],hostToDatacenter[int(datacenter[0])],float(datacenter[2])))
				
			else:
				for Id in range(int(datacenterId[0]),int(datacenterId[1])+1):
					datacenterList.append(Datacenter(Id,datacenter[1]+str(Id),hostToDatacenter[Id],float(datacenter[2])))
					
		for broker in brokers:

			brokerId = broker[0].split(',')

			if len(brokerId) == 1:
				brokerList.append(Broker(int(broker[0]),broker[1]))
			
			else:
				for Id in range(int(brokerId[0]),int(brokerId[1])+1):
					brokerList.append(Broker(Id,broker[1]+str(Id)))
		
		for vm in vms:
			
			vmId = vm[0].split(',')

			if len(vmId) == 1:
				if vm[7] == "Space Shared":
					temp = VM(int(vm[0]),vm[1],int(vm[2]),int(vm[3]),int(vm[4]),int(vm[6]),int(vm[5]),Scheduler("Cloudlet Scheduler","CloudletSpaceShared"))
					vmToBroker[int(vm[8])].append(temp)
				else:
					temp = VM(int(vm[0]),vm[1],int(vm[2]),int(vm[3]),int(vm[4]),int(vm[6]),int(vm[5]),Scheduler("Cloudlet Scheduler","CloudletTimeShared"))
					vmToBroker[int(vm[8])].append(temp)

				cloudletToVm[int(vm[0])] = temp 
				
			else: 
				for Id in range(int(vmId[0]),int(vmId[1])+1):
					if vm[7] == "Space Shared":
						temp = VM(Id,vm[1]+str(Id),int(vm[2]),int(vm[3]),int(vm[4]),int(vm[6]),int(vm[5]),Scheduler("Cloudlet Scheduler","CloudletSpaceShared"))
						vmToBroker[int(vm[8])].append(temp)
					else:
						temp = VM(Id,vm[1]+str(Id),int(vm[2]),int(vm[3]),int(vm[4]),int(vm[6]),int(vm[5]),Scheduler("Cloudlet Scheduler","CloudletTimeShared"))
						vmToBroker[int(vm[8])].append(temp)

					cloudletToVm[Id] = temp
					
		for cloudlet in cloudlets:
			
			cloudletId = cloudlet[0].split(',')

			if len(cloudletId) == 1:
				
				temp = Cloudlet(int(cloudlet[0]),cloudlet[1],int(cloudlet[2]),int(cloudlet[3]))
				
				if ',' not in cloudlet[4]:
					temp.submissionTime = int(cloudlet[4])
				
				else:
					times = cloudlet[4].split(',')
					temp.submissionTime = int(self.randomGenerator(int(times[0]),int(times[1])))

				if str(cloudlet[6]) is not '':
					temp.vmID = cloudletToVm[int(cloudlet[6])].id
				
				cloudletToBroker[int(cloudlet[5])].append(temp)
				
			else:
				for Id in range(int(cloudletId[0]),int(cloudletId[1])+1):
					temp = Cloudlet(Id,cloudlet[1]+str(Id),int(cloudlet[2]),int(cloudlet[3]))
					
					if ',' not in cloudlet[4]:
						temp.submissionTime = int(cloudlet[4])
				
					else:
						times = cloudlet[4].split(',')
						temp.submissionTime = int(self.randomGenerator(int(times[0]),int(times[1])))
					
					if str(cloudlet[6]) is not '':
						temp.vmID = cloudletToVm[int(cloudlet[6])].id
					cloudletToBroker[int(cloudlet[5])].append(temp)
					
		for broker in brokerList:
			broker.addVMList(vmToBroker[broker.uid])
			broker.addCloudletList(cloudletToBroker[broker.uid])
			
		ABC.startSimulation()
		ABC.stopSimulation()

		dataframe["brokerList"] = brokerList
		dataframe["datacenterList"] = datacenterList

		self.dataAcquired.emit(dataframe)
		self.finished.emit()

	def randomGenerator(self,start,end,size=1):

		if self.mode == "actionNormal":
			return abs(np.random.normal(start,end,size=size))

		if self.mode == "actionPoisson":
			return abs(np.random.poisson(end-start,size=size))

		if self.mode == "actionExponential":
			return abs(np.random.exponential(end-start,size=size))

		if self.mode == "actionChiSquare":
			return abs(np.random.chisquare(end-start,size=size))

		if self.mode == "actionGamma":
			return abs(np.random.gamma(end-start,size=size))

		if self.mode == "actionMarkov":
			return abs(np.random.randint(start,end,size=size))

class RunThread(QThread):

	def __init__(self,dataFile,randomGenerator,callback,threadCallback):

		super(RunThread,self).__init__()

		self.runObject = RunBody(dataFile,randomGenerator,callback)
		self.runObject.moveToThread(self)
		self.runObject.finished.connect(self.quit)
		self.started.connect(self.runObject.run)
		self.finished.connect(threadCallback)
		
		
class Graph(FigureCanvas):
	"""This class defines a embeddable matplotlib figure."""
	
	def __init__(self, parent=None, width=10, height=10, dpi=100, graph="main"):

		figure = Figure(figsize=(width, height), dpi=dpi)
		figure.subplots_adjust( left   = 0.0,
							    right  = 1.0,
							    top    = 1.0,
								bottom = 0.0,
								wspace = 1.0,
								hspace = 1.0
							  )

		super(Graph, self).__init__(figure)
		self.control = parent
		self.figure  = figure
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.axes = self.figure.add_subplot(111)
		self.figure.tight_layout()		

	def parse(self,data,data2=None,xlabel=None,ylabel=None):

		if xlabel == ylabel:
			self.line([0,1],xlabel,ylabel)
		elif data2 == None:
			self.line(data,xlabel,ylabel)
		else:
			self.bar(data,data2,xlabel,ylabel)

	def line(self,data,xlabel,ylabel):
		
		self.axes.clear()
		self.axes = self.figure.add_subplot(111)
		self.axes.set_title("".join([xlabel," vs ",ylabel]))
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		self.axes.plot(data,alpha=0.5)
		self.figure.tight_layout()	
		self.draw()

	def multiline(self,dataframe,xlabel,ylabel):

		self.axes.clear()
		self.axes = self.figure.add_subplot(111)
		self.axes.set_title("".join([xlabel," vs ",ylabel]))
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		
		i = 0
		for data in dataframe:
			self.axes.plot(data,label="".join([xlabel,str(i)]))
			i += 1
		
		self.axes.legend(loc='right', #bbox_to_anchor=(0.5, 1.05),
          				 ncol=1, fancybox=True, shadow=True)
		self.figure.tight_layout()	
		self.draw()

	def bar(self,xAxis,yAxis,xlabel,ylabel,mean=False):

		index = np.arange(len(yAxis))
		width = 0.25
		colors = ['b','r','g','y','k']
		
		startTimes = sum(xAxis)
		finishTimes = sum(yAxis)

		avg = (finishTimes - startTimes)/len(yAxis)

		self.axes.clear()
		self.axes.bar(left=index,width=width,height=yAxis,bottom=xAxis,color=colors,label=xlabel,alpha=0.5)
		
		if mean is True:
			self.axes.axhline(avg,color='k',linestyle='--',linewidth=2,alpha=0.3)
		
		self.axes.legend() 
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		self.axes.set_ylim(0)
		self.axes.set_xlim(0)
		self.axes.set_title("".join([xlabel," vs ",ylabel]))	
		
		labels =  [xlabel+str(i) for i in xrange(0,len(yAxis)+1)]
		self.axes.set_xticks(index+width)
		self.axes.set_xticklabels(labels, fontdict=None, minor=False,rotation="vertical")
		self.draw()		

	def scatter(self,xAxis,yAxis,xlabel,ylabel,connect=False):
		
		colors = np.random.rand(len(yAxis))
		
		self.axes.clear()
		self.axes = self.figure.add_subplot(111)
		self.axes.set_title("".join([xlabel," vs ",ylabel]))
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		self.axes.set_xlim(0,len(xAxis))
		self.axes.set_ylim(min(yAxis),max(yAxis))
		
		self.axes.scatter(xAxis,yAxis,c=colors,alpha=0.5)
		
		if connect is True:
			self.axes.plot(yAxis,color='k',alpha=0.5,linestyle=':')

		self.figure.tight_layout()	
		self.draw()

	def multiscatter(self,xAxis,yAxis,xlabel,ylabel):
	
		colors = np.random.rand(len(yAxis))
		
		self.axes.clear()
		self.axes = self.figure.add_subplot(111)
		self.axes.set_title("".join([xlabel," vs ",ylabel]))
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		self.axes.set_xlim(0,len(xAxis))
		self.axes.set_ylim(0,len(yAxis))
		
		it = 0
		for data in yAxis:
			self.axes.scatter([i for i in range(xAxis[it])],data,c=colors,alpha=0.5)
			it += 1

		self.figure.tight_layout()	
		self.draw()

	def histogram(self,data,xlabel,ylabel):

		pl = []

		for value in data:
			pl.append(int(value))
		
		self.axes.clear()
		self.axes = self.figure.add_subplot(111)
		self.axes.set_title("".join([xlabel," vs ",ylabel]))
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		self.axes.hist(pl,alpha=0.5,color='k',histtype='stepfilled')
		self.figure.tight_layout()	
		self.draw()

class NavigationToolbar(NavigationToolbar2QT):

	toolitems = [t for t in NavigationToolbar2QT.toolitems if
				 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

	def __init__(self, *args, **kwargs):
		
		super(NavigationToolbar,self).__init__(*args, **kwargs)
		self.layout().takeAt(4)

class Output(QObject):

    text = Signal(str)

    def write(self, text):
        self.text.emit(str(text))

class Window(QMainWindow):
		
	def __init__(self,parent = None):
		"""Initialize the main window, connect stdout and stderr to embedded text box."""
		
		QMainWindow.__init__(self,parent)
		self.setWindowIcon(QIcon("resources/ico.png"))
		
		#Just for graph
		self.cloudlet = defaultdict(list) 
		self.vm = defaultdict(list) 
		self.host = defaultdict(list)
		self.datacenter = defaultdict(list)
		self.broker = defaultdict(list)
		self.brokers = []
		self.userDict = {}

		sys.stdout = NULL()#Output()
		#sys.stderr = Output() #Decomment for release candidate
		sys.stdout.text.connect(self.output)
		#sys.stderr.text.connect(self.error) #Decomment for release candidate
		
		self.main = Ui_MainWindow()
		self.main.setupUi(self)
		
		self.setupPage()
		self.setWindowTitle('KawaiiSim')
		self.file = None
		self.initActions()
		self.new()
		self.main.hostButton.toggle() 

	def initActions(self):
		"""Initialize all actions and triggers in the GUI, connect UI and backend."""

		#Setup global radio buttons
		self.main.hostButton.toggled.connect(lambda:self.setPage(0))
		self.main.datacenterButton.toggled.connect(lambda:self.setPage(1))
		self.main.brokerButton.toggled.connect(lambda:self.setPage(2))
		self.main.vmButton.toggled.connect(lambda:self.setPage(3))
		self.main.cloudletButton.toggled.connect(lambda:self.setPage(4))
		self.main.outputButton.toggled.connect(lambda:self.setPage(5))
		self.main.errorButton.toggled.connect(lambda:self.setPage(6))
		self.main.graphButton.toggled.connect(lambda:self.setPage(7))
		self.main.previousButton.clicked.connect(self.previousPage)
		self.main.nextButton.clicked.connect(self.nextPage)
		
		self.main.hostButton.setShortcut('Ctrl+1')
		self.main.datacenterButton.setShortcut('Ctrl+2')
		self.main.brokerButton.setShortcut('Ctrl+3')
		self.main.vmButton.setShortcut('Ctrl+4')
		self.main.cloudletButton.setShortcut('Ctrl+5')
		self.main.outputButton.setShortcut('Ctrl+6')
		self.main.errorButton.setShortcut('Ctrl+7')
		self.main.graphButton.setShortcut('Ctrl+8')

		helper = {
				  0:"hostAdd",1:"hostDelete",
				  2:"datacenterAdd",3:"datacenterDelete",
				  4:"brokerAdd",5:"brokerDelete",
				  6:"vmAdd",7:"vmDelete",
				  8:"cloudletAdd",9:"cloudletDelete"	
				 }

		#Setup all pages
		page = 0
	
		for i in range(0,9,2):
			
			add = self.main.stackedWidget.widget(page).findChild(QPushButton,helper[i])
			delete = self.main.stackedWidget.widget(page).findChild(QPushButton,helper[i+1])
			add.clicked.connect(self.addRow)
			delete.clicked.connect(self.deleteRow)
			
			page += 1

		#Setup graph page
		self.setupGraph()

		#Setup actions and shortcuts
		self.distributionGroup = QActionGroup(self,exclusive=True)
		self.sortGroup = QActionGroup(self,exclusive=True)

		self.distributionGroup.addAction(self.main.actionNormal)
		self.distributionGroup.addAction(self.main.actionPoisson)
		self.distributionGroup.addAction(self.main.actionChiSquare)
		self.distributionGroup.addAction(self.main.actionGamma)
		self.distributionGroup.addAction(self.main.actionExponential)
		self.distributionGroup.addAction(self.main.actionMarkov)

		self.sortGroup.addAction(self.main.actionCloudletID)
		self.sortGroup.addAction(self.main.actionVmID)
		self.sortGroup.addAction(self.main.actionStartTime)
		self.sortGroup.addAction(self.main.actionFinishTime)
		self.sortGroup.addAction(self.main.actionSubmissionTime)
		
		self.main.actionExit.triggered.connect(self.close)
		self.main.actionExit.setShortcut('Ctrl+Q')
		
		self.main.actionSave.triggered.connect(self.save)
		self.main.actionSave.setShortcut('Ctrl+S')

		self.main.actionSaveAs.triggered.connect(self.saveAs)
		self.main.actionSaveAs.setShortcut('Ctrl+Shift+S')

		self.main.actionRun.triggered.connect(self.run)
		self.main.actionRun.setShortcut('Ctrl+R')

		self.main.actionOpen.triggered.connect(self.open)
		self.main.actionOpen.setShortcut('Ctrl+O')

		self.main.actionNew.triggered.connect(self.new)
		self.main.actionNew.setShortcut('Ctrl+Shift+N')

		self.main.actionDuplicate.triggered.connect(self.duplicate)
		self.main.actionDuplicate.setShortcut('Ctrl+Shift+C')

		self.main.actionInsertRow.triggered.connect(self.addRow)
		self.main.actionInsertRow.setShortcut('Ctrl+N')

		self.main.actionPreviousPage.triggered.connect(self.previousPage)
		self.main.actionPreviousPage.setShortcut(Qt.CTRL+Qt.Key_Left)

		self.main.actionNextPage.triggered.connect(self.nextPage)
		self.main.actionNextPage.setShortcut(Qt.CTRL+Qt.Key_Right)

		self.main.actionNormal.setChecked(True)
		self.main.actionCloudletID.setChecked(True)
		self.main.actionToggleLogs.setChecked(False)
	
	def dcIdUpdate(self,x,y):
		"""This method dynamically updates the host page with created datacenter IDs."""

		if y == 0: #Only activate if ID column was changed.

			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
			data = table.item(x,y).text()
			
			if ',' not in data: #Not using csv, single value

				table = self.main.stackedWidget.widget(0).findChild(QTableWidget)
				
				for row in range(table.rowCount()):

					datacenterId = table.cellWidget(row,8)
					dcData = []

					for index in range(datacenterId.count()):
						dcData.append(datacenterId.itemText(index))
					
					if data not in dcData:
						datacenterId.addItem(data)

			else: #Using csv, multiple datacenters created

				data = data.split(',')
				for item in range(int(data[0]),int(data[1])+1):

					table = self.main.stackedWidget.widget(0).findChild(QTableWidget)
				
					for row in range(table.rowCount()):

						datacenterId = table.cellWidget(row,8)
						dcData = []

						for index in range(datacenterId.count()):
							dcData.append(datacenterId.itemText(index))
						
						if str(item) not in dcData:
							datacenterId.addItem(str(item))

	def dcIdRemove(self):
		"""This method dynamically updates the host page with deleted datacenter IDs."""
		
		table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
		data = table.item(table.currentRow(),0).text()
		
		table = self.main.stackedWidget.widget(0).findChild(QTableWidget)
		
		if ',' not in data:
			
			for row in range(table.rowCount()):
				
	
				datacenterId = table.cellWidget(row,8)
				dcData = []

				for index in range(datacenterId.count()):
					dcData.append(datacenterId.itemText(index))
			
				if data != '':
					dcData.remove(data)

				datacenterId.clear()
				datacenterId.addItems(dcData)

		else :
			
			data = data.split(',')
			
			for item in range(int(data[0]),int(data[1])+1):
				for row in range(table.rowCount()):
	
					datacenterId = table.cellWidget(row,8)
					dcData = []

					for index in range(datacenterId.count()):
						dcData.append(datacenterId.itemText(index))
			
					if data != '':
						dcData.remove(str(item))

					datacenterId.clear()
					datacenterId.addItems(dcData)
			
			
	def brokerIdUpdate(self,x,y):

		if y == 0:

			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
			data = table.item(x,y).text()
			
			table = self.main.stackedWidget.widget(3).findChild(QTableWidget)
			
			if ',' not in data:

				for row in range(table.rowCount()):

					brokerId = table.cellWidget(row,8)
					brokerData = []

					for index in range(brokerId.count()):
						brokerData.append(brokerId.itemText(index))
					
					if data not in brokerData and data != '':
						brokerId.addItem(data)

				table = self.main.stackedWidget.widget(4).findChild(QTableWidget)
				
				for row in range(table.rowCount()):

					brokerId = table.cellWidget(row,5)
					brokerData = []

					for index in range(brokerId.count()):
						brokerData.append(brokerId.itemText(index))
					
					if data not in brokerData and data != '':
						brokerId.addItem(data)
		
			else:
				data = data.split(',')

				for item in range(int(data[0]),int(data[1])+1):

					for row in range(table.rowCount()):

						brokerId = table.cellWidget(row,8)
						brokerData = []

						for index in range(brokerId.count()):
							brokerData.append(brokerId.itemText(index))
						
						if str(item) not in brokerData and str(item) != '':
							brokerId.addItem(str(item))

					table = self.main.stackedWidget.widget(4).findChild(QTableWidget)
					
					for row in range(table.rowCount()):

						brokerId = table.cellWidget(row,5)
						brokerData = []

						for index in range(brokerId.count()):
							brokerData.append(brokerId.itemText(index))
						
						if str(item) not in brokerData and str(item) != '':
							brokerId.addItem(str(item))
		
	def brokerIdRemove(self):

		table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
		data = table.item(table.currentRow(),0).text()
		
		
		if ',' not in data:
			table = self.main.stackedWidget.widget(3).findChild(QTableWidget)
		
			for row in range(table.rowCount()):

				brokerId = table.cellWidget(row,8)
				brokerData = []

				for index in range(brokerId.count()):
					brokerData.append(brokerId.itemText(index))
			
				if data != '':
					brokerData.remove(data)

				brokerId.clear()
				brokerId.addItems(brokerData)

			table = self.main.stackedWidget.widget(4).findChild(QTableWidget)
		
			for row in range(table.rowCount()):

				brokerId = table.cellWidget(row,5)
				brokerData = []

				for index in range(brokerId.count()):
					brokerData.append(brokerId.itemText(index))
			
				if data != '':
					brokerData.remove(data)

				brokerId.clear()
				brokerId.addItems(brokerData)
		
		else:
			data = data.split(',')

			for item in range(int(data[0]),int(data[1])+1):
				table = self.main.stackedWidget.widget(3).findChild(QTableWidget)
		
				for row in range(table.rowCount()):

					brokerId = table.cellWidget(row,8)
					brokerData = []

					for index in range(brokerId.count()):
						brokerData.append(brokerId.itemText(index))
			
					if data != '':
						brokerData.remove(str(item))

					brokerId.clear()
					brokerId.addItems(brokerData)

				table = self.main.stackedWidget.widget(4).findChild(QTableWidget)
		
				for row in range(table.rowCount()):

					brokerId = table.cellWidget(row,5)
					brokerData = []

					for index in range(brokerId.count()):
						brokerData.append(brokerId.itemText(index))
			
					if data != '':
						brokerData.remove(str(item))

					brokerId.clear()
					brokerId.addItems(brokerData)					
				
	def vmIdUpdate(self,x,y):

		if y == 0:

			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
			data = table.item(x,y).text()
			
			table = self.main.stackedWidget.widget(4).findChild(QTableWidget)
			
			if ',' not in data:

				for row in range(table.rowCount()):

					vmId = table.cellWidget(row,6)
					vmData = []

					for index in range(vmId.count()):
						vmData.append(vmId.itemText(index))
					
					if data not in vmData:
						vmId.addItem(data)

			else:
				data = data.split(',')

				for item in range(int(data[0]),int(data[1])+1):
					for row in range(table.rowCount()):

						vmId = table.cellWidget(row,6)
						vmData = []

						for index in range(vmId.count()):
							vmData.append(vmId.itemText(index))
						
						if str(item) not in vmData:
							vmId.addItem(str(item))

	def vmIdRemove(self):

		table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
		data = table.item(table.currentRow(),0).text()
		
		table = self.main.stackedWidget.widget(4).findChild(QTableWidget)
		
		if ',' not in data:
		
			for row in range(table.rowCount()):

				vmId = table.cellWidget(row,6)
				vmData = []

				for index in range(vmId.count()):
					vmData.append(vmId.itemText(index))
			
				if data != '':
					vmData.remove(data)

				vmId.clear()
				vmId.addItems(vmData)
				
		else:
			data = data.split(',');
			for item in range(int(data[0]),int(data[1])+1):
				for row in range(table.rowCount()):
					vmId = table.cellWidget(row,6)
					vmData = []

					for index in range(vmId.count()):
						vmData.append(vmId.itemText(index))
			
					if data != '':
						vmData.remove(str(item))

					vmId.clear()
					vmId.addItems(vmData)			

	def addRow(self,row=None):
		"""Adds a new row to relevant page."""
		
		table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
		table.insertRow(table.rowCount())
		table.setCurrentCell(table.rowCount()-1,0)
		
		page = self.main.stackedWidget.currentIndex()
		
		if page == 0 or page == 3 or page == 4:
			for column in range(table.columnCount()-2):
				table.setItem(table.rowCount()-1,column,QTableWidgetItem(''))

		else:
			for column in range(table.columnCount()):
				table.setItem(table.rowCount()-1,column,QTableWidgetItem(''))

		if page == 0 or page == 3:
			
			scheduler = QComboBox()
			
			scheduler.addItem("Space Shared")
			scheduler.addItem("Time Shared")
			table.setCellWidget(table.rowCount()-1,table.columnCount()-2,scheduler)
			
		if page == 0:	
			
			entId = QComboBox()
			entData = []
			datacenterTable = self.main.stackedWidget.widget(1).findChild(QTableWidget) 
			
			for index in range(entId.count()):
				entData.append(entId.itemText(index))

			for row in range(datacenterTable.rowCount()):
				data = datacenterTable.item(row,0).text()
				
				if ',' not in data:
					if data not in entData and data != '':
						entId.addItem(data)

				else:
					data = data.split(',')

					for item in range(int(data[0]),int(data[1])+1):
						if str(item) not in entData and str(item) != '':
							entId.addItem(str(item))

			table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId)
					
		if page == 3:
		
			entId = QComboBox()
			entData = []
			brokerTable = self.main.stackedWidget.widget(2).findChild(QTableWidget) 
			
			for index in range(entId.count()):
				entData.append(entId.itemText(index))

			for row in range(brokerTable.rowCount()):
				data = brokerTable.item(row,0).text()
				
				if ',' not in data:
					if data not in entData and data != '':
						entId.addItem(data)

				else:
					data = data.split(',')

					for item in range(int(data[0]),int(data[1])+1):
						if str(item) not in entData and str(item) != '':
							entId.addItem(str(item))

			table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId)
			QObject.connect(table,SIGNAL("cellChanged(int,int)"),self.vmIdUpdate)
		
		if page == 1:
			QObject.connect(table,SIGNAL("cellChanged(int,int)"),self.dcIdUpdate)
		
		if page == 2:
			QObject.connect(table,SIGNAL("cellChanged(int,int)"),self.brokerIdUpdate)

		if page == 4:

			entId1 = QComboBox()
			entData = []
			brokerTable = self.main.stackedWidget.widget(2).findChild(QTableWidget) 
			
			for index in range(entId1.count()):
				entData.append(entId1.itemText(index))

			for row in range(brokerTable.rowCount()):
				
				data = brokerTable.item(row,0).text()
				
				if ',' not in data:
					if data not in entData and data != '':
						entId1.addItem(data)

				else:
					data = data.split(',')

					for item in range(int(data[0]),int(data[1])+1):
						if str(item) not in entData and str(item) != '':
							entId1.addItem(str(item))	

			entId2 = QComboBox()
			entData = []
			vmTable = self.main.stackedWidget.widget(3).findChild(QTableWidget) 
			
			entId2.addItem(None)

			for index in range(entId2.count()):
				entData.append(entId2.itemText(index))

			for row in range(vmTable.rowCount()):
				data = vmTable.item(row,0).text()
				
				if ',' not in data:
					if data not in entData and data != '':
						entId2.addItem(data)

				else:
					data = data.split(',')

					for item in range(int(data[0]),int(data[1])+1):
						if str(item) not in entData and str(item) != '':
							entId2.addItem(str(item))

			table.setCellWidget(table.rowCount()-1,table.columnCount()-2,entId1)
			table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId2)

	def deleteRow(self):

		table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
		
		if self.main.stackedWidget.currentIndex() == 1:
			self.dcIdRemove()
		if self.main.stackedWidget.currentIndex() == 2:
			self.brokerIdRemove()
		if self.main.stackedWidget.currentIndex() == 3:
			self.vmIdRemove()
		
		table.removeRow(table.currentRow())

	def save(self):
		
		data = []

		for page in range(5):

			self.main.stackedWidget.setCurrentIndex(page)
			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
			items = []
		
			if page == 0 or page == 3 or page == 4: 
				for row in range(table.rowCount()):
					for column in range(table.columnCount()-2):
						items.append(table.item(row,column).text())

					items.append(table.cellWidget(row,table.columnCount()-2).currentText())
					items.append(table.cellWidget(row,table.columnCount()-1).currentText())
					items.append('\n')
			else:
				for row in range(table.rowCount()):
					for column in range(table.columnCount()):
						items.append(table.item(row,column).text())
					
					items.append('\n')
			
			data.append(items)

		self.main.stackedWidget.setCurrentIndex(0)
		self.main.hostButton.toggle()
		
		if self.file == None:

			fileName = QFileDialog.getSaveFileName(self,'','',selectedFilter='*.sc')
			self.file = str(fileName[0])

		if self.file != '':
			
			try:
				with open(self.file,"w") as f:
					pickle.dump(data,f)
			except IOError:
				pass		
	
	def saveAs(self):

		data = []

		for page in range(5):

			self.main.stackedWidget.setCurrentIndex(page)
			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
			items = []
		
			if page == 0 or page == 3 or page == 4: 
				for row in range(table.rowCount()):
					for column in range(table.columnCount()-2):
						items.append(table.item(row,column).text())

					items.append(table.cellWidget(row,table.columnCount()-2).currentText())
					items.append(table.cellWidget(row,table.columnCount()-1).currentText())
					items.append('\n')
			else:
				for row in range(table.rowCount()):
					for column in range(table.columnCount()):
						items.append(table.item(row,column).text())
					
					items.append('\n')
			
			data.append(items)

		self.main.stackedWidget.setCurrentIndex(0)
		self.main.hostButton.toggle()
		
		fileName = QFileDialog.getSaveFileName(self,'','',selectedFilter='*.sc')
		self.file = str(fileName[0])

		if self.file != '':
			
			try:
				with open(self.file,"w") as f:
					pickle.dump(data,f)
			except IOError:
				pass

	def run(self):
		
		if self.file is None:
			self.error("RUNTIMEERROR:No simulation configuration detected, have you tried running a simulation yet?")
			self.main.errorButton.toggle()		

		else:
			
			if self.main.actionToggleLogs.isChecked():
				sys.stdout = Output()
				sys.stdout.text.connect(self.output)

			else:
				sys.stdout = NULL()
				sys.stdout.text.connect(self.output)

			self.main.outputButton.toggle()
			self.main.stackedWidget.setCurrentIndex(5)

			self.timer = QTimer()
			self.timer.timeout.connect(QCoreApplication.processEvents)

			self.save()
			self.main.stackedWidget.widget(5).findChild(QTextEdit).clear()

			self.cloudlet.clear()
			self.vm.clear()
			self.host.clear()
			self.datacenter.clear()
			self.broker.clear()
			self.userDict.clear()
			self.brokers = []

			self.runnerThread = RunThread(self.file,
							 			  self.distributionGroup.checkedAction().objectName(),
							 			  self.getGraphingData,
							 			  self.processGraphingData
							 			 ) 
			
			self.runnerThread.start()

			self.progressDialog = QProgressDialog("Running Simulation","Abort",0,0,self)
			self.progressDialog.setWindowTitle("Running..")
			self.progressDialog.setMinimumDuration(4000)
			self.progressDialog.setAutoReset(False)
			self.progressDialog.setAutoClose(False)
			self.progressDialog.setValue(1)
			self.progressDialog.show()

	def getGraphingData(self,dataframe):
		self.dataframe = dataframe

	def processGraphingData(self):

		sys.stdout = Output()
		sys.stdout.text.connect(self.output)

		for broker in self.dataframe["brokerList"]:
			broker.getCloudletData(sortby=self.getSortMode())

		for broker in self.dataframe["brokerList"]:
			broker.logCost()

		for datacenter in self.dataframe["datacenterList"]:
			datacenter.logCost()

		cloudlets = []
		vms = []
		brokers = []
		datacenters = []
		hosts = []

		#GRAPHING DATA
		for broker in self.dataframe["brokerList"]:
			
			brokers.append(broker)

			for cloudlet in broker.getRecievedCloudlets():
				cloudlets.append(cloudlet)

		for broker in sorted(brokers,key=lambda x:x.uid):	

			self.broker[broker.uid] = {"cloudlets":defaultdict(list),"vms":defaultdict(list)}
			self.broker["userCost"].append(broker.userCost)
			self.brokers.append(broker.uid)

			for cloudlet in broker.getRecievedCloudlets():

				self.broker[broker.uid]["cloudlets"]["startTimes"].append(cloudlet.startTime[0])
				self.broker[broker.uid]["cloudlets"]["finishTimes"].append(cloudlet.clockState)
				self.broker[broker.uid]["cloudlets"]["submissionTime"].append(cloudlet.submissionTime)	
				self.broker[broker.uid]["cloudlets"]["processingTime"].append(cloudlet.processingTime)

			for vm in broker.getRecievedVms():

				self.broker[broker.uid]["vms"]["startTimes"].append(0)
				self.broker[broker.uid]["vms"]["finishTimes"].append(vm.clockState)
				self.broker[broker.uid]["vms"]["tasks"].append(len(vm._cloudletList))	
				self.broker[broker.uid]["vms"]["taskArrivals"].append([cloudlet.submissionTime for cloudlet in vm._cloudletList])

		for cloudlet in sorted(cloudlets,key=lambda x:x.uid):
				
			self.cloudlet["startTimes"].append(cloudlet.startTime[0])
			self.cloudlet["finishTimes"].append(cloudlet.clockState)
			self.cloudlet["submissionTime"].append(cloudlet.submissionTime)
			self.cloudlet["processingTime"].append(cloudlet.processingTime) 
				
		for datacenter in sorted(self.dataframe["datacenterList"],key=lambda x:x.uid):
			
			for vm in datacenter.datacenterManager.getFinishedVms():
				vms.append(vm)

			for host in datacenter._hostList:
				hosts.append(host)
				
			self.datacenter["startTimes"].append(0)
			self.datacenter["finishTimes"].append(datacenter.clockState)	
			self.datacenter["totalCost"].append(datacenter.totalCost)

		for vm in sorted(vms,key=lambda x:x.uid):

			self.vm["startTimes"].append(0)
			self.vm["finishTimes"].append(vm.clockState)
			self.vm["tasks"].append(len(vm._cloudletList))
			self.vm["taskArrivals"].append([cloudlet.submissionTime for cloudlet in vm._cloudletList])
		
		for host in sorted(hosts,key=lambda x:x.uid):

			self.host["startTimes"].append(0)
			self.host["finishTimes"].append(host.clockState)
			self.host["vms"].append(len(host._vmList))
		
		self.main.outputButton.toggle()
		self.main.stackedWidget.setCurrentIndex(5)

		self.setupGraph()

		self.progressDialog.setRange(0,1)
		self.progressDialog.setValue(1)
		self.progressDialog.setLabelText("Finished Simulation.")
		self.progressDialog.setCancelButtonText("OK")

	def open(self):

		filename = QFileDialog.getOpenFileName(self,'','',filter='*.sc')

		self.file = filename[0]

		if str(self.file) != '':
			
			with open(self.file,"r") as f:
				data = pickle.load(f)

			hosts = [list(y) for x, y in groupby(data[0], lambda z: z == '\n') if not x]
			datacenters = [list(y) for x, y in groupby(data[1], lambda z: z == '\n') if not x]
			brokers = [list(y) for x, y in groupby(data[2], lambda z: z == '\n') if not x]
			vms = [list(y) for x, y in groupby(data[3], lambda z: z == '\n') if not x]
			cloudlets = [list(y) for x, y in groupby(data[4], lambda z: z == '\n') if not x]

			order = [1,2,0,3,4]
			
			for page in order:

				self.main.stackedWidget.setCurrentIndex(page)
				table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
				table.clearContents()
				table.setRowCount(0)
				self.setupPage()
			
				if page == 0:
					
					for host in hosts:
						
						table.insertRow(table.rowCount())
						i = 0
						
						for data in host:
							
							if i < 7:
								table.setItem(table.rowCount()-1,i,QTableWidgetItem(data))
							
							elif i == 7:
								scheduler = QComboBox()
								scheduler.addItem("Space Shared")
								scheduler.addItem("Time Shared")
								table.setCellWidget(table.rowCount()-1,table.columnCount()-2,scheduler)
								index = scheduler.findText(data,Qt.MatchExactly)
								scheduler.setCurrentIndex(index)
							
							else:	
								entId = QComboBox()
								entData = []
								datacenterTable = self.main.stackedWidget.widget(1).findChild(QTableWidget) 
				
								for index in range(entId.count()):
									entData.append(entId.itemText(index))

								for row in range(datacenterTable.rowCount()):
									textData = datacenterTable.item(row,0).text()
					
									if ',' not in textData:
										if textData not in entData:
											entId.addItem(textData)

									else:
										textData = textData.split(',')

										for item in range(int(textData[0]),int(textData[1])+1):
											if str(item) not in entData:
												entId.addItem(str(item))

								index = entId.findText(data,Qt.MatchExactly)
								entId.setCurrentIndex(index)

								table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId)
							
							i += 1

				if page == 1:
					for datacenter in datacenters:
						table.insertRow(table.rowCount())
						i = 0
						for data in datacenter:
							table.setItem(table.rowCount()-1,i,QTableWidgetItem(data))
							i += 1

				if page == 2:
					for broker in brokers:
						table.insertRow(table.rowCount())
						i = 0
						for data in broker:
							table.setItem(table.rowCount()-1,i,QTableWidgetItem(data))
							i += 1

				if page == 3:
					for vm in vms:
						table.insertRow(table.rowCount())
						i = 0
						for data in vm:
							
							if i < 7:
								table.setItem(table.rowCount()-1,i,QTableWidgetItem(data))
							
							elif i == 7:
								scheduler = QComboBox()
								scheduler.addItem("Space Shared")
								scheduler.addItem("Time Shared")
								table.setCellWidget(table.rowCount()-1,table.columnCount()-2,scheduler)
								index = scheduler.findText(data,Qt.MatchExactly)
								scheduler.setCurrentIndex(index)
							
							else:	
								entId = QComboBox()
								entData = []
								brokerTable = self.main.stackedWidget.widget(2).findChild(QTableWidget) 
				
								for index in range(entId.count()):
									entData.append(entId.itemText(index))

								for row in range(brokerTable.rowCount()):
									textData = brokerTable.item(row,0).text()
					
									if ',' not in textData:
										if textData not in entData:
											entId.addItem(textData)

									else:
										textData = textData.split(',')

										for item in range(int(textData[0]),int(textData[1])+1):
											if str(item) not in entData:
												entId.addItem(str(item))
								
								index = entId.findText(data,Qt.MatchExactly)
								entId.setCurrentIndex(index)

								table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId)
							
							i += 1

				if page == 4:

					for cloudlet in cloudlets:
						table.insertRow(table.rowCount())
						i = 0
						for data in cloudlet:
							
							if i < 5:
								table.setItem(table.rowCount()-1,i,QTableWidgetItem(data))
							
							elif i == 5:
								entId = QComboBox()
								entData = []
								brokerTable = self.main.stackedWidget.widget(2).findChild(QTableWidget) 
				
								for index in range(entId.count()):
									entData.append(entId.itemText(index))

								for row in range(brokerTable.rowCount()):
									textData = brokerTable.item(row,0).text()
					
									if ',' not in textData:
										if textData not in entData:
											entId.addItem(textData)

									else:
										textData = textData.split(',')

										for item in range(int(textData[0]),int(textData[1])+1):
											if str(item) not in entData:
												entId.addItem(str(item))
								
								index = entId.findText(data,Qt.MatchExactly)
								entId.setCurrentIndex(index)

								table.setCellWidget(table.rowCount()-1,table.columnCount()-2,entId)
							
							else:	
								entId2 = QComboBox()
								entData = []
								vmTable = self.main.stackedWidget.widget(3).findChild(QTableWidget) 
								
								entId2.addItem(None)

								for index in range(entId2.count()):
									entData.append(entId2.itemText(index))

								for row in range(vmTable.rowCount()):
									textData = vmTable.item(row,0).text()
									
									if ',' not in textData:
										if textData not in entData:
											entId2.addItem(textData)

									else:
										textData = textData.split(',')

										for item in range(int(textData[0]),int(textData[1])+1):
											if str(item) not in entData:
												entId2.addItem(str(item))

								index = entId2.findText(data,Qt.MatchExactly)
								entId2.setCurrentIndex(index)

								table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId2)

							i += 1

			self.main.stackedWidget.setCurrentIndex(0)
			self.main.hostButton.toggle()

	def new(self):

		for page in range(5):

			self.main.stackedWidget.setCurrentIndex(page)
			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
			table.clearContents()
			table.setRowCount(0)
			self.setupPage()
			
		self.main.stackedWidget.setCurrentIndex(0)
		self.main.hostButton.toggle()
	
	def duplicate(self):

		data = []
		page = self.main.stackedWidget.currentIndex()
	
		if page < 5:

			table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)

			if page == 0 or page == 3 or page == 4:

				for column in range(table.columnCount() - 2):
					data.append(table.item(table.currentRow(),column).text())
				data.append(table.cellWidget(table.currentRow(),table.columnCount()-2).currentText())
				data.append(table.cellWidget(table.currentRow(),table.columnCount()-1).currentText())		
			
			else:
				for column in range(table.columnCount()):
					data.append(table.item(table.currentRow(),column).text())


			table.insertRow(table.rowCount())
			
			if page == 0 or page == 3 or page == 4:
				for column in range(table.columnCount()-2):
					table.setItem(table.rowCount()-1,column,QTableWidgetItem(str(data[column])))

			else:
				for column in range(table.columnCount()):
					table.setItem(table.rowCount()-1,column,QTableWidgetItem(data[column]))

			if page == 0 or page == 3:
				
				scheduler = QComboBox()
				scheduler.addItem("Space Shared")
				scheduler.addItem("Time Shared")
				table.setCellWidget(table.rowCount()-1,table.columnCount()-2,scheduler)
				
				index = scheduler.findText(data[table.columnCount()-2],Qt.MatchExactly)
				scheduler.setCurrentIndex(index)
			
			if page == 0:	
				
				entId = QComboBox()
				entData = []
				datacenterTable = self.main.stackedWidget.widget(1).findChild(QTableWidget) 
				
				for index in range(entId.count()):
					entData.append(entId.itemText(index))

				for row in range(datacenterTable.rowCount()):
					data = datacenterTable.item(row,0).text()
					
					if ',' not in data:
						if data not in entData and data != '':
							entId.addItem(data)

					else:
						data = data.split(',')

						for item in range(int(data[0]),int(data[1])+1):
							if str(item) not in entData and str(item) != '':
								entId.addItem(str(item))

				table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId)
						
			if page == 3:
			
				entId = QComboBox()
				entData = []
				brokerTable = self.main.stackedWidget.widget(2).findChild(QTableWidget) 
				
				for index in range(entId.count()):
					entData.append(entId.itemText(index))

				for row in range(brokerTable.rowCount()):
					data = brokerTable.item(row,0).text()
					
					if ',' not in data:
						if data not in entData and data != '':
							entId.addItem(data)

					else:
						data = data.split(',')

						for item in range(int(data[0]),int(data[1])+1):
							if str(item) not in entData and str(item) != '':
								entId.addItem(str(item))

				table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId)
				
			if page == 4:

				entId1 = QComboBox()
				entData = []
				brokerTable = self.main.stackedWidget.widget(2).findChild(QTableWidget) 
				
				for index in range(entId1.count()):
					entData.append(entId1.itemText(index))

				for row in range(brokerTable.rowCount()):
					
					data = brokerTable.item(row,0).text()
					
					if ',' not in data:
						if data not in entData and data != '':
							entId1.addItem(data)

					else:
						data = data.split(',')

						for item in range(int(data[0]),int(data[1])+1):
							if str(item) not in entData and str(item) != '':
								entId1.addItem(str(item))	

				entId2 = QComboBox()
				entData = []
				vmTable = self.main.stackedWidget.widget(3).findChild(QTableWidget) 
				
				entId2.addItem(None)

				for index in range(entId2.count()):
					entData.append(entId2.itemText(index))

				for row in range(vmTable.rowCount()):
					data = vmTable.item(row,0).text()
					
					if ',' not in data:
						if data not in entData and data != '':
							entId2.addItem(data)

					else:
						data = data.split(',')

						for item in range(int(data[0]),int(data[1])+1):
							if str(item) not in entData and str(item) != '':
								entId2.addItem(str(item))

				table.setCellWidget(table.rowCount()-1,table.columnCount()-2,entId1)
				table.setCellWidget(table.rowCount()-1,table.columnCount()-1,entId2)
			
	def output(self,text):

		outputBox = self.main.stackedWidget.widget(5).findChild(QTextEdit)
		outputBox.setFont(QFont("Courier",15))
		outputBox.setReadOnly(True)
		cursor = outputBox.textCursor()
		cursor.movePosition(QTextCursor.End)
		cursor.insertText(text)
		outputBox.setTextCursor(cursor)
		
	def error(self,text):

		errorBox = self.main.stackedWidget.widget(6).findChild(QTextEdit)
		errorBox.setFont(QFont("Courier",15))
		errorBox.setReadOnly(True)
		cursor = errorBox.textCursor()
		cursor.movePosition(QTextCursor.End)
		cursor.insertText(text)
		errorBox.setTextCursor(cursor)

	def setupPage(self):
		
		table = self.main.stackedWidget.currentWidget().findChild(QTableWidget)
		table.setSelectionMode(QAbstractItemView.SingleSelection)
		header = table.horizontalHeader()
		header.setResizeMode(QHeaderView.Stretch)
		table.setToolTip("")

	def setPage(self,index):
		
		self.main.stackedWidget.setCurrentIndex(index)
		if index >= 5:
			if index == 5 or index == 6:
				text = self.main.stackedWidget.currentWidget().findChild(QTextEdit)
				text.setReadOnly(True)
		else:
			self.setupPage()
		
	def previousPage(self):

		page = self.main.stackedWidget.currentIndex()
		indexToggle = {0:self.main.hostButton.toggle,1:self.main.datacenterButton.toggle,
					   2:self.main.brokerButton.toggle,3:self.main.vmButton.toggle,
					   4:self.main.cloudletButton.toggle,5:self.main.outputButton.toggle,
					   6:self.main.errorButton.toggle,7:self.main.graphButton.toggle}
		
		indexToggle[(page-1)%8]()

	def nextPage(self):

		page = self.main.stackedWidget.currentIndex()
		indexToggle = {0:self.main.hostButton.toggle,1:self.main.datacenterButton.toggle,
					   2:self.main.brokerButton.toggle,3:self.main.vmButton.toggle,
					   4:self.main.cloudletButton.toggle,5:self.main.outputButton.toggle,
					   6:self.main.errorButton.toggle,7:self.main.graphButton.toggle}
		
		indexToggle[(page+1)%8]()

	def timerEvent(self,e):

		if self.step >= 100:

			self.timer.stop()
			return

		self.step += 1
		self.progressBar.setValue(self.step)

	def setupGraph(self):

		canvas = Graph()
		toolbar = NavigationToolbar(canvas,self)

		layout = QHBoxLayout()
		xAxis = QComboBox()
		yAxis = QComboBox()
		layout.addWidget(xAxis)
		layout.addWidget(yAxis)
		dummy = QWidget()
		dummy.setLayout(layout)
		
		xAxis.addItem("")
		xAxis.addItem("Cloudlets")
		xAxis.addItem("VMs")
		xAxis.addItem("Hosts")
		xAxis.addItem("Datacenters")
		xAxis.addItem("Brokers")
		
		self.userDict = {}

		for index in range(len(self.brokers)):
			
			xAxis.addItem("User "+str(self.brokers[index]))		
			self.userDict["User "+str(self.brokers[index])] = self.brokers[index]

		QObject.connect(xAxis,SIGNAL("currentIndexChanged(const QString&)"),lambda:self.yAxisUpdate(xAxis.currentText(),yAxis))

		button = QPushButton('Plot')
		button.clicked.connect(lambda:self.plot(canvas,xAxis,yAxis))

		layout = QVBoxLayout()
		layout.addWidget(toolbar)
		layout.addWidget(canvas)
		layout.addWidget(dummy)
		layout.addWidget(button)
		
		dummy = QWidget()
		dummy.setLayout(layout)
		self.main.stackedWidget.insertWidget(7,dummy)

	def plot(self,canvas,xSelect,ySelect):
		
		#Its a start!
		
		try:
			if str(xSelect.currentText()) == "Cloudlets":
				
				if str(ySelect.currentText()) == "Start to Finish":
					canvas.bar(self.cloudlet["startTimes"],
							   self.cloudlet["finishTimes"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )
				
				if str(ySelect.currentText()) == "Submission Time (Scatter)":
					canvas.scatter([i for i in range(len(self.cloudlet["submissionTime"]))],
								   self.cloudlet["submissionTime"],
								   xSelect.currentText(),
								   ySelect.currentText(),
								   connect=self.main.actionSCL.isChecked()
								  )
					
				if str(ySelect.currentText()) == "Submission Time (Histogram)":	
					canvas.histogram(self.cloudlet["submissionTime"],
								     xSelect.currentText(),
								     ySelect.currentText(),
								    )
				
				if str(ySelect.currentText()) == "Processing Time":
					canvas.bar([0 for _ in range(len(self.cloudlet["processingTime"]))],
						       self.cloudlet["processingTime"],
						       xSelect.currentText(),
						       ySelect.currentText(),
						       mean=self.main.actionSML.isChecked()
						      )
					
			elif str(xSelect.currentText()) == "VMs":
				
				if str(ySelect.currentText()) == "Total Uptime":
					canvas.bar(self.vm["startTimes"],
							   self.vm["finishTimes"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )
				
				if str(ySelect.currentText()) == "Total Tasks":
					canvas.bar([0 for _ in range(len(self.vm["tasks"]))],
							   self.vm["tasks"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )		

				if str(ySelect.currentText()) == "Task Arrival Times":
					canvas.multiline(self.vm["taskArrivals"],
								     xSelect.currentText(),
								     ySelect.currentText()
								    )
				
			elif str(xSelect.currentText()) == "Hosts":		
				
				if str(ySelect.currentText()) == "Total Uptime":
					canvas.bar(self.host["startTimes"],
						       self.host["finishTimes"],
						       xSelect.currentText(),
						       ySelect.currentText(),
						       mean=self.main.actionSML.isChecked()
						      )
				
				if str(ySelect.currentText()) == "VMs created":
					canvas.bar([0 for _ in range(len(self.host["vms"]))],
							   self.host["vms"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )		

			elif str(xSelect.currentText()) == "Datacenters":

				if str(ySelect.currentText()) == "Total Uptime":
					canvas.bar(self.datacenter["startTimes"],
						       self.datacenter["finishTimes"],
						       xSelect.currentText(),
						       ySelect.currentText(),
						       mean=self.main.actionSML.isChecked()
						      )
			
				if str(ySelect.currentText()) == "Total Cost":
					canvas.bar([0 for _ in range(len(self.datacenter["totalCost"]))],
							   self.datacenter["totalCost"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )	

			elif str(xSelect.currentText()) == "Brokers":

				if str(ySelect.currentText()) == "Total Cost":
					canvas.bar([0 for _ in range(len(self.broker["userCost"]))],
							   self.broker["userCost"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )	

			elif str(xSelect.currentText()) in self.userDict.keys():

				if str(ySelect.currentText()) == "Cloudlets/Start to Finish":
					canvas.bar(self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["startTimes"],
						       self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["finishTimes"],
						       xSelect.currentText(),
						       ySelect.currentText(),
						       mean=self.main.actionSML.isChecked()
						      )
				
				if str(ySelect.currentText()) == "Cloudlets/Submission Time (Scatter)":
					canvas.scatter([i for i in range(len(self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["submissionTime"]))],
								   self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["submissionTime"],
								   xSelect.currentText(),
								   ySelect.currentText(),
								   connect=self.main.actionSCL.isChecked()
								  )
				
				if str(ySelect.currentText()) == "Cloudlets/Submission Time (Histogram)":
					canvas.histogram(self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["submissionTime"],
								     xSelect.currentText(),
								     ySelect.currentText(),
								    )
				
				if str(ySelect.currentText()) == "Cloudlets/Processing Time":
					canvas.bar([0 for _ in range(len(self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["processingTime"]))],
						       self.broker[self.userDict[xSelect.currentText()]]["cloudlets"]["processingTime"],
						       xSelect.currentText(),
						       ySelect.currentText(),
						       mean=self.main.actionSML.isChecked()
						      )
				
				if str(ySelect.currentText()) == "VMs/Total Uptime":
					canvas.bar(self.broker[self.userDict[xSelect.currentText()]]["vms"]["startTimes"],
							   self.broker[self.userDict[xSelect.currentText()]]["vms"]["finishTimes"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )
				
				if str(ySelect.currentText()) == "VMs/Total Tasks":
					canvas.bar([0 for _ in range(len(self.broker[self.userDict[xSelect.currentText()]]["vms"]["tasks"]))],
							   self.broker[self.userDict[xSelect.currentText()]]["vms"]["tasks"],
							   xSelect.currentText(),
							   ySelect.currentText(),
							   mean=self.main.actionSML.isChecked()
							  )		
				
				if str(ySelect.currentText()) == "VMs/Task Arrival Times":
					canvas.multiline( self.broker[self.userDict[xSelect.currentText()]]["vms"]["taskArrivals"],
								     xSelect.currentText(),
								     ySelect.currentText()
								    )
			else:
				canvas.parse(None,None,xSelect.currentText(),ySelect.currentText())
		
		except IndexError:
			
			response = QMessageBox.critical(QWidget(),"Error","No simulation detected.")

			if response == QMessageBox.Ok:
				self.error("GRAPHERROR:No simulation detected, have you tried running a simulation yet?")
				self.main.errorButton.toggle()
	
	def yAxisUpdate(self,text,yAxis):

		if text == "":

			yAxis.clear()
			yAxis.addItem("")

		if text == "Cloudlets":
			
			yAxis.clear()
			yAxis.addItem("Start to Finish")
			yAxis.addItem("Submission Time (Scatter)")
			yAxis.addItem("Submission Time (Histogram)")
			yAxis.addItem("Processing Time")

		if text == "VMs":

			yAxis.clear()
			yAxis.addItem("Total Uptime")
			yAxis.addItem("Total Tasks")
			yAxis.addItem("Task Arrival Times")
			
		if text == "Hosts":

			yAxis.clear()
			yAxis.addItem("Total Uptime")
			yAxis.addItem("VMs created")

		if text == "Datacenters":

			yAxis.clear()
			yAxis.addItem("Total Uptime")
			yAxis.addItem("Total Cost")

		if text == "Brokers":

			yAxis.clear()
			yAxis.addItem("Total Cost")

		if text in self.userDict.keys():

			yAxis.clear()
			yAxis.addItem("Cloudlets/Start to Finish")
			yAxis.addItem("Cloudlets/Submission Time (Scatter)")
			yAxis.addItem("Cloudlets/Submission Time (Histogram)")
			yAxis.addItem("Cloudlets/Processing Time")
			yAxis.addItem("VMs/Total Uptime")
			yAxis.addItem("VMs/Total Tasks")
			yAxis.addItem("VMs/Task Arrival Times")

	def getSortMode(self):

		if self.main.actionCloudletID.isChecked():
			return "uid"

		if self.main.actionVmID.isChecked():
			return "vm.uid"

		if self.main.actionStartTime.isChecked():
			return "startTime"

		if self.main.actionFinishTime.isChecked():
			return "clockState"

		if self.main.actionSubmissionTime.isChecked():
			return "submissionTime"

	def close(self):
		exit()

def main():
	
	app = QApplication(sys.argv)
	
	if system() == "Windows":
		
		import ctypes
		
		app.setStyle("cleanlooks")
		appId = u'bmsce.kawaiisim.gui.1.0Alpha'
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
	
	window = Window()
	window.show()
	
	args = QApplication.arguments()	
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
