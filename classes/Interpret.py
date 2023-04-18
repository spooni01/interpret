import sys
import re
import classes.Operations as operations
import classes.ErrorHandler as err

class Interpret:
	app = operations.Operations()
	numberOfInstructions = 0
	initializedVars = 0
	instr = []
	label = []
	call = []
	indexOfLabel = []

	def checkVariable(self, argument):
		if argument[0] != 'var' :
			err.ErrorHandler("Variable have to been var", 32)
		try:
			argument = argument[1].split('@',1)
		except ValueError:
			err.ErrorHandler("Missing @", 32)

		if not re.match(r"^[a-zá-žA-ZÁ-Ž_\-$&%*?!][\w\-$&%*?!]*$", argument[1]):
			err.ErrorHandler("Variable is invalid", 32)
		if argument[0] not in ['LF', 'TF', 'GF']:
			err.ErrorHandler("Incorrect frame", 32)

	def symbChecker(self, argument):
		if argument[0] == 'var':
			self.checkVariable(argument)
		elif argument[0] == 'nil':
			if argument[1] != 'nil':
				err.ErrorHandler("Invalid value", 32)
		elif argument[0] == 'string':
			if argument[1] == None:
				argument[1] = ''
			elif ('#' in argument[1] or re.search(r"\s", argument[1])):
				err.ErrorHandler("Invalid STRING", 32)
			else:
				for i in range(0,len(argument[1])):
					if i == len(argument[1]):	
						break;	
					if argument[1][i] == '\\':
						try:
							tmp = argument[1][i+1] + argument[1][i+2] + argument[1][i+3]
							tmp = int(tmp)
							argument[1] = argument[1][:i] + chr(tmp) + argument[1][i+4:]
						except (ValueError, TypeError, IndexError):
							err.ErrorHandler("Invalid value of string", 32)
		elif argument[0] == 'int':
			try:
				argument[1] = int(argument[1])
			except (ValueError, TypeError, OverflowError):
				err.ErrorHandler("Invalid INT", 32)
		elif argument[0] == 'float':
			try:
				argument[1] = float.fromhex(argument[1])
			except (ValueError, TypeError):
				err.ErrorHandler("Invalid FLOAT", 32)
		elif argument[0] == 'bool':
			if argument[1] != 'true' and argument[1] != 'false':
				err.ErrorHandler("Invalid BOOL", 32)
		else:
			err.ErrorHandler("Invalid symbol", 32)

	def checkLabel(self, argument, orderedInstructions):
		if not re.match(r"^[a-zá-žA-ZÁ-Ž_\-$&%*?!][\w\-$&%*?!]*$", argument[1]):
			err.ErrorHandler("Label is invalid", 32)
		if argument[0] != 'label':
			err.ErrorHandler("Have to be label", 32)
		if orderedInstructions != -1:
			if argument[1] in self.label:
				err.ErrorHandler("Label was already defined", 52)
			else:			
				self.label.append(argument[1])
				self.indexOfLabel.append(orderedInstructions)
		
	def checkType(self, argument):
		if argument[0] != 'type':
			err.ErrorHandler("Have to be type", 32)
		if argument[1] not in ['int', 'bool', 'string', 'float']:
			err.ErrorHandler("Incorrect type", 32)

	def goToLabel(self, label, call):
		if label not in self.label: 
			err.ErrorHandler("Label is not defined", 52)
		else: 
			if call != -1:
				self.call.append(call) 
			return self.indexOfLabel[self.label.index(label)]

	def interpret(self, inputFile, inputBool):
		i = 0	
		while i < len(self.instr):
			self.numberOfInstructions += 1
			if self.instr[i][0].upper() == "MOVE":
				self.app.move(self.instr[i][1][0][1].split('@',1),
							self.instr[i][1][1])
			elif self.instr[i][0].upper() == "DEFVAR":
				self.app.defvar(self.instr[i][1][0][1].split('@',1), i)
			elif self.instr[i][0].upper() == "CALL":
				i = self.goToLabel(self.instr[i][1][0][1], i)
				self.numberOfInstructions += 1	
			elif self.instr[i][0].upper() == "RETURN":
				if self.call == []:
					err.ErrorHandler("Empty value", 56)
				else:	
					i = self.call.pop(-1)	
			elif self.instr[i][0].upper() == "CREATEFRAME":
				self.app.TF = [] 	
			elif self.instr[i][0].upper() == "PUSHFRAME":
				self.app.pushframe()
			elif self.instr[i][0].upper() == "POPFRAME":
				self.app.popframe()
			elif self.instr[i][0].upper() == "PUSHS":
				self.app.push(self.instr[i][1][0])
			elif self.instr[i][0].upper() == "POPS":
				self.app.pop(self.instr[i][1][0][1].split('@',1))
			elif self.instr[i][0].upper() == "ADD":
				self.app.calculator("ADD",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "SUB":
				self.app.calculator("SUB",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "MUL":
				self.app.calculator("MUL",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "IDIV":
				self.app.calculator("IDIV",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "DIV":
				self.app.calculator("DIV",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "LT":
				self.app.conditions("LT",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "GT":
				self.app.conditions("GT",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "EQ":
				self.app.conditions("EQ",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "AND":
				self.app.logicOperation("AND",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "OR":
				self.app.logicOperation("OR",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "NOT":
				self.app.logicOperation("NOT",self.instr[i][1][0][1].split('@',1),self.instr[i][1][1])
			elif self.instr[i][0].upper() == "READ":
				self.app.read(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1][1], inputFile, inputBool)
			elif self.instr[i][0].upper() == "WRITE":
				self.app.write(self.instr[i][1][0])
			elif self.instr[i][0].upper() == "CONCAT":
				self.app.concat(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "STRLEN":
				self.app.stringlenght(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1])
			elif self.instr[i][0].upper() == "GETCHAR":
				self.app.getchar(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "SETCHAR":
				self.app.setchar(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "TYPE":
				self.app.instrType(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1])
			elif self.instr[i][0].upper() == "INT2CHAR":
				self.app.int2Char(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1])
			elif self.instr[i][0].upper() == "FLOAT2INT":
				self.app.float2Int(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1])
			elif self.instr[i][0].upper() == "INT2FLOAT":
				self.app.int2Float(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1])
			elif self.instr[i][0].upper() == "STRI2INT":
				self.app.stri2Int(self.instr[i][1][0][1].split('@',1),self.instr[i][1][1],self.instr[i][1][2])
			elif self.instr[i][0].upper() == "LABEL":
				pass 
			elif self.instr[i][0].upper() == "JUMP":
				i = self.goToLabel(self.instr[i][1][0][1], -1)
				self.numberOfInstructions += 1	
			elif self.instr[i][0].upper() == "JUMPIFEQ":
				tmpBool = self.app.jumpsConditions("JUMPIFEQ", self.instr[i][1][1],self.instr[i][1][2])
				if tmpBool == True:
					i = self.goToLabel(self.instr[i][1][0][1], -1)
					self.numberOfInstructions += 1
			elif self.instr[i][0].upper() == "JUMPIFNEQ":
				tmpBool = self.app.jumpsConditions("JUMPIFNEQ", self.instr[i][1][1],self.instr[i][1][2])
				if tmpBool == True:	
					i = self.goToLabel(self.instr[i][1][0][1], -1)
					self.numberOfInstructions += 1
			elif self.instr[i][0].upper() == "EXIT":
				exitVal = self.app.instrExit(self.instr[i][1][0])
				self.initializedVars = self.app.numberOfVars
				return exitVal
			elif self.instr[i][0].upper() == "DPRINT":
				self.app.dprint(self.instr[i][1][0])
			elif self.instr[i][0].upper() == "BREAK":
				justToBeExact = 'th'	
				if i == 1:
					justToBeExact = 'st'
				elif i == 2:
					justToBeExact = 'nd'
				elif i == 3:
					justToBeExact = 'rd'
				sys.stderr.write("""Instruction:				{0}{6} of {7}
								Count of executed instr: 	{1}
								Data stack:	{2}
								Global Frame:	{3}
								Temporary Frame:	{4}
								Local Frame:	{5}
								""".format(i +1,self.numberOfInstructions -1, self.app.dataStack, self.app.GF,self.app.TF, self.app.LF,justToBeExact,len(self.instr)))
			elif self.instr[i][0].upper() == "CLEARS":
				self.app.dataStack = []	
			elif self.instr[i][0].upper() == "LTS":
				self.app.conditions("LT",None,None,None,True)
			elif self.instr[i][0].upper() == "GTS":
				self.app.conditions("GT",None,None,None,True)
			elif self.instr[i][0].upper() == "EQS":
				self.app.conditions("EQ",None,None,None,True)
			elif self.instr[i][0].upper() == "ANDS":
				self.app.logicOperation("AND",None,None,None,True)
			elif self.instr[i][0].upper() == "ORS":
				self.app.logicOperation("OR",None,None,None,True)
			elif self.instr[i][0].upper() == "NOTS":
				self.app.logicOperation("NOT",None,None,None,True)
			elif self.instr[i][0].upper() == "ADDS":
				self.app.calculator("ADDS",None,None,None,True)
			elif self.instr[i][0].upper() == "SUBS":
				self.app.calculator("SUBS",None,None,None,True)
			elif self.instr[i][0].upper() == "MULS":
				self.app.calculator("MULS",None,None,None,True)
			elif self.instr[i][0].upper() == "DIVS":
				self.app.calculator("DIVS",None,None,None,True)
			elif self.instr[i][0].upper() == "IDIVS":
				self.app.calculator("IDIVS",None,None,None,True)
			elif self.instr[i][0].upper() == "INT2CHARS":
				self.app.int2Char(None, None, True)
			elif self.instr[i][0].upper() == "STRI2INTS":
				self.app.stri2Int(None, None, None, True)
			elif self.instr[i][0].upper() == "INT2FLOATS":
				self.app.int2Float(None, None, True)
			elif self.instr[i][0].upper() == "FLOAT2INTS":
				self.app.float2Int(None, None, True)
			elif self.instr[i][0].upper() == "JUMPIFEQS":
				tmpBool = self.app.jumpsConditions("JUMPIFEQ", None, None, True)
				if tmpBool == True:
					i = self.goToLabel(self.instr[i][1][0][1], -1)
					self.numberOfInstructions += 1
			elif self.instr[i][0].upper() == "JUMPIFNEQS":
				tmpBool = self.app.jumpsConditions("JUMPIFNEQ", None, None, True)
				if tmpBool == True:
					i = self.goToLabel(self.instr[i][1][0][1], -1)
					self.numberOfInstructions += 1
			i += 1
		self.initializedVars = self.app.numberOfVars
		return 0

	def isCountRight(self, instr, currectNumber, mustNumber):
		if currectNumber != mustNumber:
			err.ErrorHandler("Incorrect number of arguments", 32)
			
	def isInstructionCorrect(self, order, instrList):
		for i in range(0,len(instrList)):
			orderedInstructions = order[i][0]
			instructionList = [ "MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME","DEFVAR","EQ", "AND", "OR", "NOT", "INT2CHAR", "CALL","RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "DIV","LT", "GT", "STRI2INT", "INT2FLOAT", "FLOAT2INT","READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ","EXIT", "DPRINT", "BREAK","CLEARS","ADDS", "SUBS", "MULS", "IDIVS", "DIVS","LTS", "GTS", "EQS","ANDS", "ORS", "NOTS","INT2CHARS", "STRI2INTS", "INT2FLOATS", "FLOAT2INTS","JUMPIFEQS", "JUMPIFNEQS" ]						
			
			
			if instrList[orderedInstructions][0].upper() not in instructionList:
				err.ErrorHandler("Instruction list not exist", 32)
			try:
				if instrList[orderedInstructions][0].upper() == "MOVE":
					self.isCountRight(instrList[orderedInstructions][0], len(instrList[orderedInstructions]) - 1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "CREATEFRAME":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "PUSHFRAME":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "POPFRAME":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "ADD":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "SUB":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "MUL":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "IDIV":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "DIV":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "DEFVAR":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkVariable(instrList[orderedInstructions][1])
				elif instrList[orderedInstructions][0].upper() == "CALL":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkLabel(instrList[orderedInstructions][1], -1)
				elif instrList[orderedInstructions][0].upper() == "RETURN":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "PUSHS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.symbChecker(instrList[orderedInstructions][1])
				elif instrList[orderedInstructions][0].upper() == "POPS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkVariable(instrList[orderedInstructions][1])
				elif instrList[orderedInstructions][0].upper() == "LT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "GT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "EQ":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "AND":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "OR":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "NOT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "READ":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.checkType(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "WRITE":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.symbChecker(instrList[orderedInstructions][1])
				elif instrList[orderedInstructions][0].upper() == "CONCAT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "STRLEN":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "GETCHAR":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "SETCHAR":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "TYPE":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "LABEL":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkLabel(instrList[orderedInstructions][1], i)
				elif instrList[orderedInstructions][0].upper() == "INT2CHAR":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "FLOAT2INT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "INT2FLOAT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 2)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
				elif instrList[orderedInstructions][0].upper() == "STRI2INT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkVariable(instrList[orderedInstructions][1])
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "JUMP":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkLabel(instrList[orderedInstructions][1], -1)
				elif instrList[orderedInstructions][0].upper() == "JUMPIFEQ":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkLabel(instrList[orderedInstructions][1], -1)
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "JUMPIFNEQ":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 3)
					self.checkLabel(instrList[orderedInstructions][1], -1)
					self.symbChecker(instrList[orderedInstructions][2])
					self.symbChecker(instrList[orderedInstructions][3])
				elif instrList[orderedInstructions][0].upper() == "EXIT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.symbChecker(instrList[orderedInstructions][1])
				elif instrList[orderedInstructions][0].upper() == "DPRINT":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.symbChecker(instrList[orderedInstructions][1])
				elif instrList[orderedInstructions][0].upper() == "BREAK":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "CLEARS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "ADDS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "SUBS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "MULS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "DIVS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "IDIVS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "LTS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "GTS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "EQS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "ANDS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "ORS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "JUMPIFNEQS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkLabel(instrList[orderedInstructions][1], -1)
				elif instrList[orderedInstructions][0].upper() == "NOTS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "INT2CHARS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "STRI2INTS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "INT2FLOATS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "FLOAT2INTS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 0)
				elif instrList[orderedInstructions][0].upper() == "JUMPIFEQS":
					self.isCountRight(instrList[orderedInstructions][0] ,len(instrList[orderedInstructions]) -1, 1)
					self.checkLabel(instrList[orderedInstructions][1], -1)

				temp = [instrList[order[i][0]][0], instrList[order[i][0]][1:]]
				self.instr.append(temp)
			except IndexError:
				err.ErrorHandler("Wrong arguments in instruction", 32)