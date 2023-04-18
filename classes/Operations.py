import sys

#
import ippcode_bank as ib
#


# Operations for instructions
class Operations:
	def __init__(self):
		self.stackFrame = []	
		self.TF = None				#temporary frame
		self.LF = None				#local frame
		self.GF = []				#global frame
		self.dataStack = []		
		self.initializedVars = 0	#STATI extension, stores count of initialized vars
		self.readValue = []			#variable for handling READ instruction
		self.defVarIndex = []		#to prevent errors in loops
		self.TFinit = []			#for STATI extension counts ever defined vars in TF
		self.LFinit = []			#for STATI extension counts ever defined vars in LF


	#pushes TF to LF
	def pushFrame(self):
		if self.TF != None:
			self.stackFrame.append(self.TF)
			self.LF = self.TF
			self.TF = None
		else:
			raise ib.FrameError("Temporary frame 'TF' does not exist")


	#pops frame from stackFrame to temporary frame
	def popFrame(self):
		if len(self.stackFrame) != 0:
			self.TF = self.stackFrame.pop(-1)
			try:
				self.LF = self.stackFrame[-1]
			except IndexError:
				self.LF = None
		else:
			raise ib.FrameError("Could not execute POPFRAME, frame stack is already empty")


	#gets variable in 'arg' from the GF
	#returns index where it is in corresponding stack 
	#and the variable -> a list with ['type', 'name', 'value']
	def getFromGF(self,var):	#returns index if found + the found var and type, if not found returns -1
		if self.GF == []:
			return -1, []
		index = 0
		for name in self.GF:
			if var == name[1]:
				return index, name	
			index += 1
		return -1, []		


	#gets variable in 'arg' from the LF
	#returns index where it is in corresponding stack 
	#and the variable -> a list with ['type', 'name', 'value']
	def getFromLF(self,var):
		if self.LF == None:
			raise ib.FrameError("Local frame 'LF' does not exist")
		index = 0
		for name in self.LF:
			if name[1] == var:
				return index, name
			index += 1
		return -1, []		


	#gets variable in 'arg' from the TF
	#returns index where it is in corresponding stack 
	#and the variable -> a list with ['type', 'name', 'value']
	def getFromTF(self,var):
		if self.TF == None:
			raise ib.FrameError("Temporary frame 'TF' does not exist")
		index = 0
		for name in self.TF:
			if name[1] == var:
				return index, name
			index += 1
		return -1, []	


	# declares variable in wanted frame
	#var[0] is the frame, var[1] is the variable name
	def defVar(self, var, index):
		if var[0] == "GF":
			if index in self.defVarIndex:
				return
			else:
				self.defVarIndex.append(index)
			found, foundvar = self.getFromGF(var[1])
			if found != -1: 	
				raise ib.SemanticsError("redefinition of var '{0}' in '{1}'".format(var[1], var[0]))  
			else:
				typeAndVar = ["", var[1], "noValue"]	#['type', 'name', 'value']
				self.GF.append(typeAndVar)
		elif var[0] == "TF":
			found, foundvar = self.getFromTF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0}' in '{1}'".format(var[1], var[0]))
			else:
				typeAndVar = ["", var[1], "noValue"]
				self.TF.append(typeAndVar)
		elif var[0] == "LF":
			found, foundvar = self.getFromLF(var[1])
			if found != -1:
				raise ib.SemanticsError("redefinition of var '{0} in '{1}'".format(var[1], var[0]))
			else:
				typeAndVar = ["", var[1], "noValue"]
				self.LF.append(typeAndVar)


	#finds the var[1] in the frame var[0]
	# if its symbol, the symbBool is True
	def foundVar(self, var, symbBool):
		found = -1
		foundVar = []
		if symbBool == True:
			if var[0] == 'var':
				var = var[1].split('@',1)
			else:
				foundVar = [var[0], [], var[1]]
				return found, foundVar

		if var[0] == "GF":
			found, foundVar = self.getFromGF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0]))  
		elif var[0] == "TF":
			found, foundVar = self.getFromTF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0])) 
		elif var[0] == "LF":
			found, foundVar = self.getFromLF(var[1])
			if found == -1:
				raise ib.UndefinedVar("var '{0}' in '{1}' is not defined".format(var[1], var[0]))
		return found, foundVar


	#sets the type and value to variable
	#frame = wanted frame
	#index = location where the var is in the frame stack
	#typeVar = the wanted type for var
	#value = the wanted value for variable
	def setTypeValue(self, frame, index, typeVar, value):
		if frame == "GF":
			self.GF[index][0] = typeVar
			self.GF[index][2] = value
		elif frame == "TF":
			self.TF[index][0] = typeVar
			self.TF[index][2] = value
		elif frame == "LF":
			self.LF[index][0] = typeVar
			self.LF[index][2] = value


	#sets value and type from symb to the variable var
	def move(self, var, symb):
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == '':	#this means that no type was previously specified
			raise ib.MissingValue("unitialized variable")
		self.isInitialized(var)
		self.setTypeValue(var[0],varIndex,symbFound[0], symbFound[2])


	#adds data from symb to dataStack
	def pushs(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		appendSymb = [symbFound[0], symbFound[2]]
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		self.dataStack.append(appendSymb)


	#pops the top of the dataStack to variable var
	#if stack == True it just pops to popSymb and returns it
	def pops(self, var = None, stack = False):
		if self.dataStack == []:
			raise ib.MissingValue("instruction POPS cannot be executed: data stack is empty")
		if stack == True:
			popSymb = self.dataStack.pop(-1)
			return popSymb
		varIndex, varFound = self.foundVar(var, False)
		popSymb = self.dataStack.pop(-1) 
		if popSymb[0] == '':
			raise ib.MissingValue("unitialized variable")
		self.isInitialized(var)
		self.setTypeValue(var[0], varIndex, popSymb[0], popSymb[1])


	#executes the Arithmetic operations
	#op = wanted Arithmetic operations
	#var = where the result will be saved 
	#symb1 = operator 1
	#symb2 = operator 2
	#if stack == True, the result will be pushed to dataStack and not saved to var
	def calculate(self, op, var, symb1, symb2, stack = False):
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			symb2 = self.pops(None,True)
			symb1 = self.pops(None,True)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		if stack == False:
			self.isInitialized(var)
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symb1Found[0] != 'int' and symb1Found[0] != 'float': 
			if symb1Found[1] == []:
				varOrSymb = 'symb'
			else:
				varOrSymb = 'var: ' + symb1Found[1]
			raise ib.WrongArgTypes(
				"operand ({3})'{0}' of type '{1}' is not of the correct type for operation '{2}'".format(
				symb1Found[2], symb1Found[0], op, varOrSymb))
		if symb2Found[0] != 'int' and symb2Found[0] != 'float':
			if symb2Found[1] == []:
				varOrSymb = 'symb'
			else:
				varOrSymb = 'var: ' + symb2Found[1]
			raise ib.WrongArgTypes(
			"operand ({3})'{0}' of type '{1}' is not of the correct type for operation '{2}'".format(
				symb2Found[2], symb2Found[0], op, varOrSymb))		
		if (symb1Found[0] == 'int' and symb2Found[0] == 'int') or (symb1Found[0] == 'float' and symb2Found[0] == 'float'):
			pass
		else:
			raise ib.WrongArgTypes(
			"Could not execute {2}. Operands ({1})'{0}' and ({4})'{3}' should be both of the same type - No implicit conversions".format(
				symb1Found[2], symb1Found[0], op, symb2Found[2], symb2Found[0]))	
		if op == 'ADD' or op == 'ADDS':
			if isinstance(symb1Found[2] + symb2Found[2], int):
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] + symb2Found[2])
				else:
					self.pushs(['int', symb1Found[2] + symb2Found[2]])
			else:
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'float', symb1Found[2] + symb2Found[2])
				else:
					self.pushs(['float', symb1Found[2] + symb2Found[2]])
		elif op == 'SUB' or op == 'SUBS':
			if isinstance(symb1Found[2] - symb2Found[2], int):
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] - symb2Found[2])
				else:
					self.pushs(['int', symb1Found[2] - symb2Found[2]])
			else:
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'float', symb1Found[2] - symb2Found[2])
				else:
					self.pushs(['float', symb1Found[2] - symb2Found[2]])
		elif op == 'MUL' or op == 'MULS':
			if isinstance(symb1Found[2] * symb2Found[2], int):
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] * symb2Found[2])
				else:
					self.pushs(['int', symb1Found[2] * symb2Found[2]])
			else:
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'float', symb1Found[2] * symb2Found[2])
				else:
					self.pushs(['float', symb1Found[2] * symb2Found[2]])
		elif op == 'IDIV' or op == 'IDIVS':
			try:
				if isinstance(symb1Found[2] // symb2Found[2], int):
					if stack == False:
						self.setTypeValue(var[0],varIndex, 'int', symb1Found[2] // symb2Found[2])
					else:
						self.pushs(['int', symb1Found[2] // symb2Found[2]])
				else:
					if stack == False:
						self.setTypeValue(var[0],varIndex, 'float', symb1Found[2] // symb2Found[2])
					else:
						self.pushs(['float', symb1Found[2] + symb2Found[2]])
			except ZeroDivisionError:
				raise ib.WrongValue("Zero division error")
		elif op == 'DIV' or op == 'DIVS':
			try:
				if stack == False:
					self.setTypeValue(var[0],varIndex, 'float', symb1Found[2] / symb2Found[2])
				else:
					self.pushs(['float', symb1Found[2] / symb2Found[2]])
			except ZeroDivisionError:
				raise ib.WrongValue("Zero division error")


	#executes the relational operations
	#op = wanted relational operations
	#var = where the bool result will be saved 
	#symb1 = operator 1
	#symb2 = operator 2
	#if stack == True, the result will be pushed to dataStack and not saved to var
	def conditions(self, op, var, symb1, symb2, stack = False):
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			symb2 = self.pops(None,True)
			symb1 = self.pops(None,True)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)	
		if stack == False:
			self.isInitialized(var)
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symb1Found[0] != symb2Found[0] or (symb1Found[0] == 'nil' or symb2Found[0] == 'nil'):
			if op == 'EQ' and (symb1Found[0] == 'nil' or symb2Found[0] == 'nil'):
				pass
			else:
				raise ib.WrongArgTypes(
				"different types for relational instructions, '{0}'('{1}') '{2}'('{3}')".format(
					symb1Found[2],symb1Found[0],symb2Found[2], symb2Found[0]))
		if symb1Found[0] == 'bool':
			if symb1Found[2] == 'true':
				symb1Found[2] = True
			else:
				symb1Found[2] = False
		if symb2Found[0] == 'bool':
			if symb2Found[2] == 'true':
				symb2Found[2] = True
			else:
				symb2Found[2] = False
		result = ''	#final result which will be in the var, or pushed to dataStack
		if op == 'LT':
			if symb1Found[2] < symb2Found[2]:
				result = True
			else:
				result = False
		elif op == 'GT':
			if symb1Found[2] > symb2Found[2]:
				result = True
			else:
				result = False
		elif op == 'EQ':
			if symb1Found[2] == 'nil' or symb2Found[2] == 'nil':
				if symb1Found[2] == symb2Found[2]:
					result = True
				else:
					result = False
			else:
				if symb1Found[2] == symb2Found[2]:
					result = True
				else:
					result = False
		if result == True:
			if stack == False:
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
			else:
				self.pushs(['bool', 'true'])
		elif result == False:
			if stack == False:
				self.setTypeValue(var[0],varIndex, 'bool', 'false')
			else:
				self.pushs(['bool', 'false'])


	#executes the logical operations
	#op = wanted logical operations
	#var = where the bool result will be saved 
	#symb1 = operator 1
	#symb2 = operator 2
	#if stack == True, the result will be pushed to dataStack and not saved to var
	def logical(self, op, var, symb1, symb2 = [], stack = False):	
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			if op != 'NOT':
				symb2 = self.pops(None,True)
			symb1 = self.pops(None,True)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Found = ['bool', ["nothing"]]	#just because of 'NOT' uses only 2 args
		if stack == False:
			self.isInitialized(var)
		if op != 'NOT':
			symb2Index, symb2Found = self.foundVar(symb2, True)	
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if op == 'NOT' and symb1Found[0] != 'bool':
			raise ib.WrongArgTypes(
			"Logical operations need bool type, not '{0}'('{1}')".format(
				symb1Found[2],symb1Found[0]))
		elif symb1Found[0] != 'bool' or symb2Found[0] != 'bool':
			raise ib.WrongArgTypes(
			"Logical operations need bool type, not '{0}'('{1}') '{2}'('{3}')".format(
				symb1Found[2],symb1Found[0],symb2Found[2], symb2Found[0]))	
		result = ''	#final result which will be in the var, or pushed to dataStack
		if op == 'AND':
			if symb1Found[2] == 'true' and symb2Found[2] == 'true':
				result = True
			else:
				result = False
		elif op == 'OR':
			if symb1Found[2] == 'true' or symb2Found[2] == 'true':
				result = True
			else:
				result = False
		elif op == 'NOT':
			if symb1Found[2] == 'true':
				result = False
			else:
				result = True
		if result == True:
			if stack == False:
				self.setTypeValue(var[0],varIndex, 'bool', 'true')
			else:
				self.pushs(['bool', 'true'])
		elif result == False:
			if stack == False:
				self.setTypeValue(var[0],varIndex, 'bool', 'false')
			else:
				self.pushs(['bool', 'false'])


	#JUMPIFEQ and JUMPIFNEQ implementation, 
	#returns true or false depends on symb1 and symb2
	def condJumps(self, op, symb1, symb2, stack = False):
		if stack == True:
			symb2 = self.pops(None,True)
			symb1 = self.pops(None,True)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)	
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symb1Found[0] != symb2Found[0]:
			if symb1Found[0] == 'nil' or symb2Found[0] == 'nil':
				pass
			else:
				raise ib.WrongArgTypes(
				"different types for relational instructions, '{0}'('{1}') '{2}'('{3}')".format(
					symb1Found[2],symb1Found[0],symb2Found[2], symb2Found[0]))	
		if symb1Found[2] == 'nil' or symb2Found[2] == 'nil':
			if symb1Found[2] == symb2Found[2]:
				if op == 'JUMPIFEQ':
					return True
				else:
					return False
			else:
				if op == 'JUMPIFEQ':
					return False
				else:
					return True
		else:
			if symb1Found[2] == symb2Found[2]:
				if op == 'JUMPIFEQ':
					return True
				else:
					return False
			else:
				if op == 'JUMPIFEQ':
					return False
				else:
					return True


	#reads input data from stdin via input() or via file 
	#from sys.arg --input and saves the value to the var
	def read(self, var, typeValue, inputFile, inputBool):
		varIndex, varFound = self.foundVar(var, False)
		self.isInitialized(var)
		try:
			if inputBool == True:	#we read from the actual file
				if self.readValue == []:
					self.readValue = open(inputFile, "r")
					self.readValue = self.readValue.read()
					#split so every READ gets what it was meant to get
					self.readValue = str(self.readValue).split('\n')
				if self.readValue != []:
					if isinstance(self.readValue, str):
						readValueNow = self.readValue
						self.readValue = ''
					else: 
						#gradually pops the line from the line
						readValueNow = self.readValue.pop(0)
			else: 
				readValueNow = input()	#get the value from STDIN
			try:
				if typeValue == 'int':
					self.setTypeValue(var[0],varIndex, 'int', int(readValueNow))
				elif typeValue == 'float':
					self.setTypeValue(var[0],varIndex, 'int', float.fromhex(readValueNow))
				elif typeValue == 'string':
					self.setTypeValue(var[0],varIndex, 'string', readValueNow)
				elif typeValue == 'bool':
					if readValueNow.upper() == 'TRUE':
						self.setTypeValue(var[0],varIndex, 'bool', 'true')
					else:
						self.setTypeValue(var[0],varIndex, 'bool', 'false')
			except (ValueError,OverflowError, TypeError):	
				raise ib.WrongArgTypes("Wrong type for READ. You set you wanted '%s'" % typeValue)
		except (EOFError, ValueError, IndexError):
			self.setTypeValue(var[0],varIndex, 'nil', 'nil')


	#prints value from symb to STDOUT 
	def write(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symbFound[0] == 'nil':
			print('',end='')
		elif symbFound[0] == 'bool':
			if symbFound[2] == 'true':
				print('true',end='')
			else:
				print('false',end='')
		elif symbFound[0] == 'int':
			print(symbFound[2],end='')
		elif symbFound[0] == 'float':
			print(float.hex(symbFound[2]),end='')
		elif symbFound[0] == 'string':
			print(symbFound[2],end='')


	#concatenation of symb1 and symb2, the result is saved to var. must be string type
	def concat(self, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		self.isInitialized(var)
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symb1Found[0] == 'string' and symb2Found[0] == 'string':
			self.setTypeValue(var[0],varIndex, 'string', symb1Found[2] + symb2Found[2])
		else:
			raise ib.WrongArgTypes("CONCAT needs two string arguments.")


	#finds length of string and saves length to var
	#var[0] is the wanted frame var[1] is the variable name
	#symb is the string from which we want the length
	def strlen(self,var,symb):
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		self.isInitialized(var)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symbFound[0] == 'string' and symbFound[2] != None:
			self.setTypeValue(var[0],varIndex, 'int', len(symbFound[2]))
		else:
			raise ib.WrongArgTypes("STRLEN needs string argument.")


	#saves the character from string in symb1 on symb2 index and 
	#saves it into var
	def getchar(self, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		self.isInitialized(var)
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symb1Found[0] == 'string' and symb2Found[0] == 'int':
			try:
				if symb2Found[2] < 0:
					raise ib.StringError("Index error, in function GETCHAR index '{0}' is out of range of '{1}'".format(
					symb2Found[2], symb1Found[2]))
				self.setTypeValue(var[0],varIndex, 'string', symb1Found[2][symb2Found[2]])
			except IndexError:
				raise ib.StringError("Index error, in function GETCHAR index '{0}' is out of range of '{1}'".format(
					symb2Found[2], symb1Found[2]))
		else:
			raise ib.WrongArgTypes("GETCHAR needs first argument string, second arguments int.")


	#replaces the character in symb2[0] to string in var on symb1 index  
	def setchar(self, var, symb1, symb2):
		varIndex, varFound = self.foundVar(var, False)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		self.isInitialized(var)
		if varFound[0] == '' or symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if varFound[0] == 'string' and symb1Found[0] == 'int' and symb2Found[0] == 'string':
			try:
				if symb1Found[2] < 0:
					raise ib.StringError(
					"Index error, in function SETCHAR index '{0}' is out of range of '{1}'".format(
					symb1Found[2], varFound[2]))
				varFound[2][symb1Found[2]] #just to raise exception
				result = varFound[2][:symb1Found[2]] + symb2Found[2][0] + varFound[2][symb1Found[2]+1:]
				self.setTypeValue(var[0], varIndex, 'string', result)
			except (IndexError, TypeError):
				raise ib.StringError(
					"Index error, in function SETCHAR index '{0}' is out of range of '{1}'".format(
					symb1Found[2], varFound[2]))
		else:
			raise ib.WrongArgTypes(
				"SETCHAR needs variable of type string, first symbol of type int, second symbol of type string")

	#dynamically gets the the type of var
	def instrType(self, var, symb):
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		self.isInitialized(var)
		if symbFound[0] == '':
			self.setTypeValue(var[0], varIndex, 'string', '')
		elif symbFound[0] == 'nil':
			self.setTypeValue(var[0], varIndex, 'string', 'nil')
		elif symbFound[0] == 'bool':
			self.setTypeValue(var[0], varIndex, 'string', 'bool')
		elif symbFound[0] == 'int':
			self.setTypeValue(var[0], varIndex, 'string', 'int')
		elif symbFound[0] == 'string':
			self.setTypeValue(var[0], varIndex, 'string', 'string')
		elif symbFound[0] == 'float':
			self.setTypeValue(var[0], varIndex, 'string', 'float')


	# ends program with the exit code saved in symb
	#returns the exit value
	def instrExit(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symbFound[0] != 'int':
			raise ib.WrongArgTypes("value for EXIT should be int in range 0-49, not '%s'" % symbFound[2])
		elif (symbFound[2] < 0 or symbFound[2] > 49):
			raise ib.WrongValue("value for EXIT should be int in range 0-49, not '%s'" % symbFound[2])
		else:
			return symbFound[2]


	#prints symb to STDERR
	def dprint(self, symb):
		symbIndex, symbFound = self.foundVar(symb, True)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		sys.stderr.write("%s" % symbFound[2])


	#convert int in symb to char and saves to var
	#if stack == True the char is pushed to dataStack
	def int2Char(self, var, symb, stack = False):
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			symb = self.pops(None,True)
		symbIndex, symbFound = self.foundVar(symb, True)
		if stack == False:
			self.isInitialized(var)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symbFound[0] != 'int':
			raise ib.WrongArgTypes(
				"INT2CHAR needs variable of type int, not '%s'" % symbFound[0])
		try:
			if stack == False:
				self.setTypeValue(var[0], varIndex, 'string', chr(symbFound[2]))
			else:
				self.pushs(['string', chr(symbFound[2])])
		except (UnicodeEncodeError, ValueError, OverflowError):
			raise ib.StringError(
				"UnicodeEncodeError. Could not encode string in INT2CHAR, '%s' value is invalid" % symbFound[2])


	#convert character in string symb1 on index symb2 to int and saves to var
	#if stack == True the int value is pushed to dataStack
	def stri2Int(self, var, symb1, symb2, stack = False):
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			symb2 = self.pops(None,True)
			symb1 = self.pops(None,True)
		symb1Index, symb1Found = self.foundVar(symb1, True)
		symb2Index, symb2Found = self.foundVar(symb2, True)
		if stack == False:
			self.isInitialized(var)
		if symb1Found[0] == '' or symb2Found[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symb1Found[0] != 'string':
			raise ib.WrongArgTypes(
				"STRI2INT needs symbol 1 of type 'string', not '%s'" % symb1Found[0])
		if symb2Found[0] != 'int':
			raise ib.WrongArgTypes(
				"STRI2INT needs symbol 2 of type int, not '%s'" % symb2Found[0])
		try:
			if symb2Found[2] < 0:
				raise ib.StringError(
					"Could not decode string in STRI2INT, '{1}' index is outside the given string '{0}'".format(
					symb1Found[2], symb2Found[2]))
			if stack == False:
				self.setTypeValue(var[0], varIndex, 'int', ord(symb1Found[2][symb2Found[2]]))
			else:
				self.pushs(['int', ord(symb1Found[2][symb2Found[2]])])
		except (TypeError, IndexError, ValueError):
			raise ib.StringError(
				"Could not decode string in STRI2INT, '{1}' index is outside the given string '{0}'".format(
					symb1Found[2], symb2Found[2]))


	#convert int in symb to float and saves to var
	#if stack == True the float value is pushed to dataStack
	def int2Float(self, var, symb, stack = False):
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			symb = self.pops(None,True)
		symbIndex, symbFound = self.foundVar(symb, True)
		if stack == False:
			self.isInitialized(var)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symbFound[0] != 'int':
			raise ib.WrongArgTypes(
				"INT2FLOAT needs variable of type int, not '%s'" % symbFound[0])
		try:
			if stack == False:
				self.setTypeValue(var[0], varIndex, 'float', float(symbFound[2]))
			else:
				self.pushs(['float', float(symbFound[2])])
		except (ValueError, TypeError):
			raise ib.WrongValue("Could not convert Int to Float")


	#convert flaot in symb to int and saves to var
	#if stack == True the int value is pushed to dataStack
	def float2Int(self, var, symb, stack = False):
		if stack == False:
			varIndex, varFound = self.foundVar(var, False)
		else:
			symb = self.pops(None,True)
		varIndex, varFound = self.foundVar(var, False)
		symbIndex, symbFound = self.foundVar(symb, True)
		if stack == False:
			self.isInitialized(var)
		if symbFound[0] == '':
			raise ib.MissingValue("unitialized variable")
		if symbFound[0] != 'float':
			raise ib.WrongArgTypes(
				"FLOAT2INT needs variable of type float, not '%s'" % symbFound[0])
		try:
			if stack == False:
				self.setTypeValue(var[0], varIndex, 'int', int(symbFound[2]))
			else:
				self.pushs(['int', int(symbFound[2])])
		except (ValueError, TypeError):
			raise ib.WrongValue("Could not convert Float to Int")

	# checks if variable var is being initialized, for statistics of number of 
	def isInitialized(self, var):
		varIndex, varFound = self.foundVar(var, False)
		if varFound[0] == '':	#this means it was just declared
			if var[0] == "TF":
				if var[1] not in self.TFinit:
					self.TFinit.append(var[1])
				else: return
			elif var[0] =="LF":	 
				if var[1] not in self.LFinit:
					self.LFinit.append(var[1])
				else: return
			self.initializedVars += 1




		