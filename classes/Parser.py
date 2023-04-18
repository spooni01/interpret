import xml.etree.ElementTree as elemTree
import classes.ErrorHandler as err

# Parse file/stdin
class Parser:
	source = None
	root = None
	listOfNumbers = []
	listofInstructions = []
	instructionCount = 0

	def __init__(self, source):
		self.source = source

	# Function will check format of XML
	def check(self):
		xmlTree = elemTree.parse(self.source)
		self.root = xmlTree.getroot()

		self.headChecker()
		self.bodyChecker()
		return self.listOfNumbers, self.listofInstructions
	
	# Checking head of XML
	def headChecker(self):
		self.checkHeadAtributtes(self.root.attrib, self.root.tag)
		for attr, value in self.root.attrib.items():
			if attr == "language":
				if value.upper() != "IPPCODE23":
					err.ErrorHandler("Language is not IPPcode23", 32)
			elif attr != "name" and attr != "description":
				err.ErrorHandler("Program can contain only: language, name, description", 32)
		
	# Checking body of XML
	def bodyChecker(self):
		for i in self.root:
			self.checkArgumentsOfInstruction(i)
			self.instructionCount = 0
			argument_1 = []
			argument_2 = []
			argument_3 = []
			instr = []
			instr.append(i.get('opcode'))
			
			# For cycle store arguments order
			for arg in i:
				self.instructionCount += 1
				self.checkArgumentFormat(i, arg)
				if int(arg.tag[3:]) == 1:
					argument_1 = [arg.get('type'), arg.text]
				elif int(arg.tag[3:]) == 2:
					argument_2 = [arg.get('type'), arg.text]
				elif int(arg.tag[3:]) == 3:
					argument_3 = [arg.get('type'), arg.text]

			self.correctOrderOfInstructions(instr,argument_1,argument_2,argument_3)

		self.sortOrder()

	# Function will check if attribute has correct language and tag
	def checkHeadAtributtes(self,attr,tag):
		if "language" not in attr:
			err.ErrorHandler("Attribute language not found", 32)
		if tag != "program":
			err.ErrorHandler("Element root must be 'program'", 32)

	# Funtion will check own arguments of instruction
	def checkArgumentsOfInstruction(self,instruction):
		if (instruction.tag != "instruction"):
			err.ErrorHandler("Root can have only <instruction>", 32)
		if (instruction.get('order') == None or instruction.get('opcode') == None):
			err.ErrorHandler("Instruction have to have: order, opcode", 32)

	# Function will check arguments format
	def checkArgumentFormat(self, i, arg):
		if (arg.tail and arg.tail.strip() != "") or (i.text and i.text.strip() != ""):
			err.ErrorHandler("Wrong XML format", 32)
		if (arg.get('type') == None):
			err.ErrorHandler("Arguments have to have type", 32)
		if (arg.get('type') not in ["int", "bool", "string", "label", "var", "type", "nil", "float"]):
			err.ErrorHandler("Incorrect type of argument", 32)
		if (arg.tag[:3] != "arg"):
			err.ErrorHandler("Incorrect argument name", 32)
		if (arg.tag[3:] not in ['1', '2', '3']):
			err.ErrorHandler("Incorrect argument number", 32)

	# Function will save in listofInstruction correct order
	def correctOrderOfInstructions(self,instr,argument_1,argument_2,argument_3):
		argNum = 0

		if argument_1 != []:
			instr.append(argument_1)
			argNum = 1

		if argument_2 != []:
			instr.append(argument_2)
			argNum = 2

		if argument_3 != []:
			instr.append(argument_3)
			argNum = 3
			
		if argNum != self.instructionCount:
			err.ErrorHandler("Wrong number of argument", 32)
		self.listofInstructions.append(instr)	#appends to listofInstructions a list with ['instruction', [its args]]

	# Function wil sort order
	def sortOrder(self):
		for i in range(0,len(self.root)):
			try:
				if int(self.root[i].get('order')) in self.listOfNumbers:
					err.ErrorHandler("Two or more arguments have same order number", 32)

				self.listOfNumbers.append(int(self.root[i].get('order')))
				if int(self.root[i].get('order')) <= -1:
					err.ErrorHandler("Order number is lower than zero", 32)
			except (ValueError, TypeError):
				err.ErrorHandler("Wrong type of order", 32)
		
		self.listOfNumbers = sorted(enumerate(self.listOfNumbers), key=lambda x: x[1])
