import sys
import classes.ErrorHandler as err

# Operations for instructions
class Operations:
	numberOfVars = 0
	TF = None
	LF = None
	GF = []
	stackFrame= []
	stackData = []
	valueReader = []
	variableNum = []

	initializationOfTF = []
	initializationOfLF = []
	
	# For each IPPcode23 function is defined own function
	def defvar(self, variable, i):
		if variable[0] == "GF":
			if i in self.variableNum:
				return
			else:
				self.variableNum.append(i)
			count, tmpArr = self.getGF(variable[1])
		elif variable[0] == "TF":
			count, tmpArr = self.getTF(variable[1])
		elif variable[0] == "LF":
			count, tmpArr = self.getLF(variable[1])
			
		if count != -1: 	
			err.ErrorHandler("Redefined var", 52)
		else:
			tmp = ["", variable[1], "noValue"]
			self.GF.append(tmp)

	def foundvar(self, variable, sym):
		count = -1
		variables = []
		if sym == True:
			if variable[0] == 'var':
				variable = variable[1].split('@',1)
			else:
				variables = [variable[0], [], variable[1]]
				return count, variables

		isErr = False
		if variable[0] == "GF":
			count, variables = self.getGF(variable[1])
			if count == -1:
				isErr = True
		elif variable[0] == "TF":
			count, variables = self.getTF(variable[1])
			if count == -1:
				isErr = True
		elif variable[0] == "LF":
			count, variables = self.getLF(variable[1])
			if count == -1:
				isErr = True
			
		if isErr:
			err.ErrorHandler("Variable '{0}' ('{1}') is not defined".format(variable[0], variable[1]), 54) 
		
		return count, variables

	def pushframe(self):
		if self.TF == None:
			err.ErrorHandler("Frame 'TF' undefined", 55)
		else:
			self.stackFrame.append(self.TF)
			self.LF = self.TF
			self.TF = None

	def popframe(self):
		if len(self.stackFrame) == 0:
			err.ErrorHandler("Problem with executing POPFRAME", 55)
		else:
			self.TF = self.stackFrame.pop(-1)
			try:
				self.LF = self.stackFrame[-1]
			except IndexError:
				self.LF = None


	def push(self, symb):
		tmp, savedSymb = self.foundvar(symb, True)
		newSymb = [savedSymb[0], savedSymb[2]]
		if savedSymb[0] == '':
			err.ErrorHandler("Variable is not initialized", 56) 
		self.stackData.append(newSymb)

	def pop(self, variable = None, saveToStack = False):
		if self.stackData == []:
			err.ErrorHandler("Stack is empty", 56) 
		if saveToStack == True:
			return self.stackData.pop(-1)
		index, tmpDel = self.foundvar(variable, False)
		popedSymb = self.stackData.pop(-1) 
		if popedSymb[0] == '':
			err.ErrorHandler("Variable is not initialized", 56) 
		self.isInit(variable)
		self.settype(variable[0], index, popedSymb[0], popedSymb[1])

	def checkCalculatorVariables(self, symbOne, symbTwo, saveToStack, variable):
		if saveToStack == False:
			self.isInit(variable)
		if symbOne == '' or symbTwo == '':
			err.ErrorHandler("Not initialized data", 56)
		if (symbOne != 'int' and symbOne != 'float') or (symbTwo != 'int' and symbTwo != 'float'): 
			err.ErrorHandler("Wrong type of variable", 53)
		
		if (symbOne == 'int' and symbTwo == 'int') or (symbOne == 'float' and symbTwo == 'float'):
			return
		else:
			err.ErrorHandler("Variables have different types", 53)

	def calculator_add(self, symbOne, symbTwo, saveToStack, var, index):
		if isinstance(symbOne + symbTwo, int):
			if saveToStack == False:
				self.settype(var,index, 'int', symbOne + symbTwo)
			else:
				self.push(['int', symbOne + symbTwo])
		else:
			if saveToStack == False:
				self.settype(var,index, 'float', symbOne + symbTwo)
			else:
				self.push(['float', symbOne + symbTwo])
	
	def calculator_sub(self, symbOne, symbTwo, saveToStack, var, index):
		if isinstance(symbOne - symbTwo, int):
			if saveToStack == False:
				self.settype(var,index, 'int', symbOne - symbTwo)
			else:
				self.push(['int', symbOne + symbTwo])
		else:
			if saveToStack == False:
				self.settype(var,index, 'float', symbOne - symbTwo)
			else:
				self.push(['float', symbOne - symbTwo])

	def calculator_mul(self, symbOne, symbTwo, saveToStack, var, index):
		if isinstance(symbOne * symbTwo, int):
			if saveToStack == False:
				self.settype(var,index, 'int', symbOne * symbTwo)
			else:
				self.push(['int', symbOne + symbTwo])
		else:
			if saveToStack == False:
				self.settype(var,index, 'float', symbOne * symbTwo)
			else:
				self.push(['float', symbOne * symbTwo])

	def calculator_idiv(self, symbOne, symbTwo, saveToStack, var, index):
		try:
			if isinstance(symbOne // symbTwo, int):
				if saveToStack == False:
					self.settype(var,index, 'int', symbOne // symbTwo)
				else:
					self.push(['int', symbOne + symbTwo])
			else:
				if saveToStack == False:
					self.settype(var,index, 'float', symbOne // symbTwo)
				else:
					self.push(['float', symbOne // symbTwo])
		except ZeroDivisionError:
			err.ErrorHandler("Zero division", 57) 

	def calculator_div(self, symbOne, symbTwo, saveToStack, var, index):
		try:
			if saveToStack == False:
				self.settype(var,index, 'float', symbOne / symbTwo)
			else:
				self.push(['float', symbOne / symbTwo])
		except ZeroDivisionError:
			err.ErrorHandler("Zero division", 57) 

	def calculator(self, operant, variable, symbOne, symbTwo, saveToStack = False):
		if saveToStack == False:
			indexOfVar, tmp = self.foundvar(variable, False)
		else:
			symbTwo = self.pop(None,True)
			symbOne = self.pop(None,True)
		tmp, symbolOne = self.foundvar(symbOne, True)
		tmp, symbolTwo = self.foundvar(symbTwo, True)
		self.checkCalculatorVariables(symbolOne[0], symbolTwo[0], saveToStack, variable)

		if operant == 'ADD' or operant == 'ADDS':
			self.calculator_add(symbolOne[2], symbolTwo[2], saveToStack, variable[0], indexOfVar)
		elif operant == 'SUB' or operant == 'SUBS':
			self.calculator_sub(symbolOne[2], symbolTwo[2], saveToStack, variable[0], indexOfVar)
		elif operant == 'MUL' or operant == 'MULS':
			self.calculator_mul(symbolOne[2], symbolTwo[2], saveToStack, variable[0], indexOfVar)
		elif operant == 'IDIV' or operant == 'IDIVS':
			self.calculator_idiv(symbolOne[2], symbolTwo[2], saveToStack, variable[0], indexOfVar)
		elif operant == 'DIV' or operant == 'DIVS':
			self.calculator_div(symbolOne[2], symbolTwo[2], saveToStack, variable[0], indexOfVar)

	def conditions(self, operand, var, symbOne, symbTwo, saveToStack = False):
		res = ''

		if saveToStack == False:
			index, tmp = self.foundvar(var, False)
		else:
			symbTwo = self.pop(None,True)
			symbOne = self.pop(None,True)
		tmp, symb1Data = self.foundvar(symbOne, True)
		tmp, symb2Data = self.foundvar(symbTwo, True)	
		if symb1Data[0] == '' or symb2Data[0] == '':
			err.ErrorHandler("Not initialized data", 56)
		if saveToStack == False:
			self.isInit(var)
		if (symb1Data[0] == 'nil' or symb2Data[0] == 'nil') or (symb1Data[0] != symb2Data[0]):
			if (symb1Data[0] == 'nil' or symb2Data[0] == 'nil') and operand == 'EQ':
				pass
			else:
				err.ErrorHandler("Relational instructions error", 53)
		if symb2Data[0] == 'bool':
			if symb2Data[2] == 'true':
				symb2Data[2] = True
			else:
				symb2Data[2] = False
		if symb1Data[0] == 'bool':
			if symb1Data[2] == 'true':
				symb1Data[2] = True
			else:
				symb1Data[2] = False
				
		if operand == 'GT':
			if symb1Data[2] > symb2Data[2]:
				res = True
			else:
				res = False
		elif operand == 'EQ':
			if symb1Data[2] != 'nil' or symb2Data[2] != 'nil':
				if symb1Data[2] == symb2Data[2]:
					res = True
				else:
					res = False				
			else:
				if symb1Data[2] == symb2Data[2]:
					res = True
				else:
					res = False

		if res == True:
			if saveToStack != False:
				self.push(['bool', 'true'])
			else:
				self.settype(var[0],index, 'bool', 'true')				
		elif res == False:
			if saveToStack != False:
				self.push(['bool', 'false'])
			else:
				self.settype(var[0],index, 'bool', 'false')

	def logicOperation(self, operant, variable, symbOne, symbTwo = [], saveToStack = False):	
		res = ''	

		if saveToStack == False:
			index, tmp = self.foundvar(variable, False)
		else:
			if operant != 'NOT':
				symbTwo = self.pop(None,True)
			symbOne = self.pop(None,True)

		tmp, symb1Data = self.foundvar(symbOne, True)
		symb2Data = ['bool', ["nothing"]]	
		if operant != 'NOT':
			symb2Index, symb2Data = self.foundvar(symbTwo, True)
		if saveToStack == False:
			self.isInit(variable)	
		if symb1Data[0] == '' or symb2Data[0] == '':
			err.ErrorHandler("Unitialized", 56)
		if (operant == 'NOT' and symb1Data[0] != 'bool') or (symb1Data[0] != 'bool' or symb2Data[0] != 'bool'):
			err.ErrorHandler("Variable have to be boolean", 53)

		if operant == 'AND':
			if symb1Data[2] == 'true' and symb2Data[2] == 'true':
				res = True
			else:
				res = False
		elif operant == 'NOT':
			if symb1Data[2] == 'true':
				res = False
			else:
				res = True
		elif operant == 'OR':
			if symb1Data[2] == 'true' or symb2Data[2] == 'true':
				res = True
			else:
				res = False

		if res == True:
			if saveToStack == False:
				self.settype(variable[0],index, 'bool', 'true')
			else:
				self.push(['bool', 'true'])
		elif res == False:
			if saveToStack == False:
				self.settype(variable[0],index, 'bool', 'false')
			else:
				self.push(['bool', 'false'])

	def concat(self, variable, symbOne, symbTwo):
		index, varData = self.foundvar(variable, False)
		tmp, symb1Data = self.foundvar(symbOne, True)
		tmp, symb2Data = self.foundvar(symbTwo, True)
		self.isInit(variable)
		if symb1Data[0] == '' or symb2Data[0] == '':
			err.ErrorHandler("Unitialized value", 56)
		if symb1Data[0] != 'string' or symb2Data[0] != 'string':
			err.ErrorHandler("CONCAT have to have two strings", 53)
		else:			
			self.settype(variable[0],index, 'string', symb1Data[2] + symb2Data[2])

	def stringlenght(self,variable,symb):
		index, tmp = self.foundvar(variable, False)
		tmp, symbData = self.foundvar(symb, True)
		self.isInit(variable)
		if symbData[0] == '':
			err.ErrorHandler("Unitialized value", 56)

		if symbData[0] == 'string' and symbData[2] != None:
			self.settype(variable[0],index, 'int', len(symbData[2]))
		else:
			err.ErrorHandler("STRLEN have to have argument string", 53)

	def jumpsConditions(self, operand, symbOne, symbTwo, saveToStack = False):
		if saveToStack == True:
			symbTwo = self.pop(None,True)
			symbOne = self.pop(None,True)
		tmp, symbOneData = self.foundvar(symbOne, True)
		tmp, symbTwoData = self.foundvar(symbTwo, True)
		
		if symbOneData[0] == '' or symbTwoData[0] == '':
			err.ErrorHandler("Unitialized variable", 56)
		if symbOneData[0] != symbTwoData[0]:
			if symbOneData[0] == 'nil' or symbTwoData[0] == 'nil':
				pass
			else:
				err.ErrorHandler("Different types", 53)
		if symbOneData[2] == 'nil' or symbTwoData[2] == 'nil':
			if symbOneData[2] == symbTwoData[2]:
				if operand == 'JUMPIFEQ':
					return True
				else:
					return False
			else:
				if operand == 'JUMPIFEQ':
					return False
				else:
					return True
		else:
			if symbOneData[2] == symbTwoData[2]:
				if operand == 'JUMPIFEQ':
					return True
				else:
					return False
			else:
				if operand == 'JUMPIFEQ':
					return False
				else:
					return True
				
	def read(self, variable, valType, file, bool):
		index, tmp = self.foundvar(variable, False)
		self.isInit(variable)
		try:
			if bool == True:	
				if self.valueReader == []:
					self.valueReader = open(file, "r")
					self.valueReader = self.valueReader.read()
					self.valueReader = str(self.valueReader).split('\n')
				if self.valueReader != []:
					if isinstance(self.valueReader, str):
						valueReaderNew = self.valueReader
						self.valueReader = ''
					else: 
						valueReaderNew = self.valueReader.pop(0)
			else: 
				valueReaderNew = input()	

			try:
				if valType == 'int':
					self.settype(variable[0],index, 'int', int(valueReaderNew))
				elif valType == 'bool':
					if valueReaderNew.upper() == 'TRUE':
						self.settype(variable[0],index, 'bool', 'true')
					else:
						self.settype(variable[0],index, 'bool', 'false')
				elif valType == 'float':
					self.settype(variable[0],index, 'int', float.fromhex(valueReaderNew))
				elif valType == 'string':
					self.settype(variable[0],index, 'string', valueReaderNew)
			except (ValueError,OverflowError, TypeError):	
				err.ErrorHandler("Incorrect type for READ", 53)
		except (IndexError, EOFError, ValueError):
			self.settype(variable[0],index, 'nil', 'nil')

	def write(self, symb):
		tmp, symbData = self.foundvar(symb, True)
		if symbData[0] == '':
			err.ErrorHandler("Unitialized value", 56)

		if symbData[0] == 'nil':
			print('',end='')
		elif symbData[0] == 'int':
			print(symbData[2],end='')
		elif symbData[0] == 'float':
			print(float.hex(symbData[2]),end='')
		elif symbData[0] == 'string':
			print(symbData[2],end='')
		elif symbData[0] == 'bool':
			if symbData[2] == 'true':
				print('true',end='')
			else:
				print('false',end='')
	
	def getchar(self, variable, symbOne, symbTwo):
		index, tmp = self.foundvar(variable, False)
		tmp, symb1Data = self.foundvar(symbOne, True)
		tmp, symb2Data = self.foundvar(symbTwo, True)
		self.isInit(variable)
		if symb1Data[0] == '' or symb2Data[0] == '':
			err.ErrorHandler("Unitialized value", 56)

		if symb1Data[0] != 'string' or symb2Data[0] != 'int':
			err.ErrorHandler("Check GETCHAR argument rule", 53)		
		else:
			if symb2Data[2] < 0:
				err.ErrorHandler("In function GETCHAR", 58)
			self.settype(variable[0],index, 'string', symb1Data[2][symb2Data[2]])

	
	def int2Char(self, variable, symb, saveToStack = False):
		if saveToStack == False:
			index, varData = self.foundvar(variable, False)
		else:
			symb = self.pop(None,True)
		symbIndex, symbData = self.foundvar(symb, True)
		if saveToStack == False:
			self.isInit(variable)
		if symbData[0] == '':
			err.ErrorHandler("Unitialized value", 56)
		if symbData[0] != 'int':
			err.ErrorHandler("Variable must be INT", 53)

		try:
			if saveToStack != False:
				self.push(['string', chr(symbData[2])])
			else:
				self.settype(variable[0], index, 'string', chr(symbData[2]))				
		except (OverflowError, UnicodeEncodeError, ValueError):
			err.ErrorHandler("Problem in int to char converting", 58)

	def stri2Int(self, variable, symbOne, symbTwo, saveToStack = False):
		if saveToStack == False:
			index, varData = self.foundvar(variable, False)
		else:
			symbTwo = self.pop(None,True)
			symbOne = self.pop(None,True)

		tmp, symb1Data = self.foundvar(symbOne, True)
		tmp, symb2Data = self.foundvar(symbTwo, True)
		if saveToStack == False:
			self.isInit(variable)
		if symb1Data[0] == '' or symb2Data[0] == '':
			err.ErrorHandler("Unitialized value", 56)
		if symb1Data[0] != 'string' or symb2Data[0] != 'int':
			err.ErrorHandler("Wrong argument", 53)

		try:
			if symb2Data[2] < 0:
				err.ErrorHandler("Problem in string to int converting", 58)
			if saveToStack != False:
				self.push(['int', ord(symb1Data[2][symb2Data[2]])])
			else:
				self.settype(variable[0], index, 'int', ord(symb1Data[2][symb2Data[2]]))
		except (ValueError, TypeError, IndexError):
			err.ErrorHandler("Problem in string to int converting", 58)

	def setchar(self, variable, symbOne, symbTwo):
		index, varData = self.foundvar(variable, False)
		symb1Index, symb1Data = self.foundvar(symbOne, True)
		tmp, symb2Data = self.foundvar(symbTwo, True)
		self.isInit(variable)
		if varData[0] == '' or symb1Data[0] == '' or symb2Data[0] == '':
			err.ErrorHandler("Unitialized value", 56)

		if varData[0] == 'string' and symb1Data[0] == 'int' and symb2Data[0] == 'string':
			try:
				if symb1Data[2] < 0:
					err.ErrorHandler("SETCHAR", 58)
				varData[2][symb1Data[2]] 
				res = varData[2][:symb1Data[2]] + symb2Data[2][0] + varData[2][symb1Data[2]+1:]
				self.settype(variable[0], index, 'string', res)
			except (IndexError, TypeError):
				err.ErrorHandler("SETCHAR", 58)
		else:
			err.ErrorHandler("Check SETCHAR argument rule", 53)

	def instrType(self, variable, symb):
		i, varData = self.foundvar(variable, False)
		tmp, symbData = self.foundvar(symb, True)
		self.isInit(variable)

		if symbData[0] == '':
			self.settype(variable[0], i, 'string', '')
		elif symbData[0] == 'int':
			self.settype(variable[0], i, 'string', 'int')
		elif symbData[0] == 'string':
			self.settype(variable[0], i, 'string', 'string')
		elif symbData[0] == 'float':
			self.settype(variable[0], i, 'string', 'float')
		elif symbData[0] == 'nil':
			self.settype(variable[0], i, 'string', 'nil')
		elif symbData[0] == 'bool':
			self.settype(variable[0], i, 'string', 'bool')
	
	def instrExit(self, symb):
		tmp, symbData = self.foundvar(symb, True)
		if symbData[0] == '':
			err.ErrorHandler("Unitialized value", 56)

		if symbData[0] != 'int':
			err.ErrorHandler("Exit value have to be int", 53)
		elif (symbData[2] < 0 or symbData[2] > 49):
			err.ErrorHandler("Exit value have to be int beetwen 0 and 49", 53)
		else:
			return symbData[2]

	def dprint(self, symb):
		tmp, symbData = self.foundvar(symb, True)
		if symbData[0] == '':
			err.ErrorHandler("Unitialized value", 56)
		sys.stderr.write("%s" % symbData[2])
	
	def int2Float(self, variable, symb, saveToStack = False):
		if saveToStack == False:
			var, tmp = self.foundvar(variable, False)
		else:
			symb = self.pop(None,True)
		tmp, founded = self.foundvar(symb, True)
		if saveToStack == False:
			self.isInit(variable)
		if founded[0] == '':
			err.ErrorHandler("Variable is not initialized", 56)
		if founded[0] != 'int':
			err.ErrorHandler("Variable is not int", 53)

		if saveToStack != False:
			self.push(['float', float(founded[2])])
		else:
			self.settype(variable[0], var, 'float', float(founded[2]))

	def float2Int(self, variable, symb, saveToStack = False):
		if saveToStack == False:
			var, tmp = self.foundvar(variable, False)
		else:
			symb = self.pop(None,True)
		var, tmp = self.foundvar(variable, False)
		symbIndex, founded = self.foundvar(symb, True)
		if saveToStack == False:
			self.isInit(variable)
		if founded[0] == '':
			err.ErrorHandler("Variable is not initialized", 56)
		if founded[0] != 'float':
			err.ErrorHandler("Variable is not float", 53)
		
		if saveToStack != False:
			self.push(['int', int(founded[2])])
		else:
			self.settype(variable[0], var, 'int', int(founded[2]))
	
	def isInit(self, var):
		tmp, variable = self.foundvar(var, False)
		if variable[0] == '':
			if var[0] =="LF":	 
				if var[1] not in self.initializationOfLF:
					self.initializationOfLF.append(var[1])
				else: return
			elif var[0] == "TF":
				if var[1] not in self.initializationOfTF:
					self.initializationOfTF.append(var[1])
				else: return
			self.numberOfVars += 1

	def getGF(self,variable):
		i = 0

		if self.GF == []:
			return -1, []
		else:
			for elem in self.GF:
				if variable == elem[1]:
					return i, elem	
				i += 1
			return -1, []	

	def getLF(self,variable):
		i = 0

		if self.LF == None:
			err.ErrorHandler("Undefined LF frame", 55)
		else:
			for elem in self.LF:
				if elem[1] == variable:
					return i, elem
				i += 1
			return -1, []		

	def getTF(self,variable):
		i = 0
		if self.TF == None:
			err.ErrorHandler("Undefined TF frame", 55)
		else:
			for elem in self.TF:
				if elem[1] == variable:
					return i, elem
				i += 1
			return -1, []	
		
	def settype(self, frame, i, type, value):
		if frame == "TF":
			self.TF[i][0] = type
			self.TF[i][2] = value
		elif frame == "GF":
			self.GF[i][0] = type
			self.GF[i][2] = value
		elif frame == "LF":
			self.LF[i][0] = type
			self.LF[i][2] = value

	def move(self, variable, symb):
		indexOdVar, tmp = self.foundvar(variable, False)
		tmp, savedSymb = self.foundvar(symb, True)
		if savedSymb[0] == '':
			err.ErrorHandler("Varieble is not initialized", 56) 	
		self.isInit(variable)
		self.settype(variable[0],indexOdVar,savedSymb[0], savedSymb[2])		