import re
import xml.etree.ElementTree as elemTree
import classes.Operations as operations
import sys

#List of all supported instructions
INSTRUCTIONS =[ "MOVE", 
				"CREATEFRAME", "PUSHFRAME", "POPFRAME", 
				"DEFVAR", 
				"CALL", 
				"RETURN", 
				"PUSHS", "POPS", 
				"ADD", "SUB", 
				"MUL", "IDIV", "DIV", 								#FLOAT extension
				"LT", "GT", "EQ", 
				"AND", "OR", "NOT", 
				"INT2CHAR", "STRI2INT", "INT2FLOAT", "FLOAT2INT", 	#FLOAT extension
				"READ", "WRITE", 
				"CONCAT", "STRLEN", 
				"GETCHAR", "SETCHAR", 
				"TYPE", 
				"LABEL", 
				"JUMP", "JUMPIFEQ", "JUMPIFNEQ",
				"EXIT", 
				"DPRINT", 
				"BREAK",
				"CLEARS",											#STATI extension
				"ADDS", "SUBS", "MULS", "IDIVS", "DIVS", 			#STATI,FLOAT extension
				"LTS", "GTS", "EQS", 								#STATI extension
				"ANDS", "ORS", "NOTS", 								#STATI extension
				"INT2CHARS", "STRI2INTS", "INT2FLOATS", "FLOAT2INTS",#STATI,FLOAT extension
				"JUMPIFEQS", "JUMPIFNEQS" ]							#STATI extension


'''
Class for Interpret which does all the job
Checks if semantics is correct 
it is connected to operations where are stored all the data and frames
This is the brain of the whole interpret
'''
class Interpret:
	def __init__(self):
		self.instructions = []	#stores all instructions from XMLfile in the right order
		self.labels = []		#stores all unique labels
		self.calls = []			#stack for CALL instruction
		self.labelIndex = []	#saves index of LABEL opcode in the correct order, so it saves time
		self.run = operations.Operations()	
		self.instrCount = 0		#count of all executed instructions
		self.initVars = 0		#count of all initialized variables

	#checks if the instrucion has the right count of needed arguments
	#countGiven is the arg count from the input XML
	#neededCount is the expected arg count for instruction instr
	def checkArgCount(self, instr, countGiven, neededCount):
		if countGiven == neededCount:
			pass
		else:
			raise ParseError("wrong number of arguments '{0}' needs '{1}' not '{2}' args".format(instr, neededCount, countGiven))

	#checks all instructions and their arguments, if they contain the right value
	#order is the instruction order in which will the instructions be executed
	#xmlInstr is the list of instructions and its arguments
	def checkInstr(self, order, xmlInstr):
		for i in range(0,len(xmlInstr)):
			# ind = order[i][0] gives the index of instruction in xmlInstr in right order
			ind = order[i][0]
			if xmlInstr[ind][0].upper() not in INSTRUCTIONS:
				raise ParseError("'%s' instruction does not exist" % xmlInstr[ind][0])
			try:
					#case insensitive instructions
				if xmlInstr[ind][0].upper() == "MOVE":
					self.checkArgCount(xmlInstr[ind][0], len(xmlInstr[ind]) - 1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "CREATEFRAME":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "PUSHFRAME":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "POPFRAME":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "DEFVAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkVar(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "CALL":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				elif xmlInstr[ind][0].upper() == "RETURN":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "PUSHS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "POPS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkVar(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "ADD":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "SUB":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "MUL":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "IDIV":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "DIV":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "LT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "GT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "EQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "AND":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "OR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "NOT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "INT2CHAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "FLOAT2INT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "INT2FLOAT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "STRI2INT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "READ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkType(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "WRITE":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "CONCAT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "STRLEN":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "GETCHAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "SETCHAR":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "TYPE":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 2)
					self.checkVar(xmlInstr[ind][1])
					self.checkSymb(xmlInstr[ind][2])
				elif xmlInstr[ind][0].upper() == "LABEL":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], i)
				elif xmlInstr[ind][0].upper() == "JUMP":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				elif xmlInstr[ind][0].upper() == "JUMPIFEQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkLabel(xmlInstr[ind][1], -1)
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "JUMPIFNEQ":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 3)
					self.checkLabel(xmlInstr[ind][1], -1)
					self.checkSymb(xmlInstr[ind][2])
					self.checkSymb(xmlInstr[ind][3])
				elif xmlInstr[ind][0].upper() == "EXIT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "DPRINT":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkSymb(xmlInstr[ind][1])
				elif xmlInstr[ind][0].upper() == "BREAK":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "CLEARS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "ADDS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "SUBS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "MULS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "DIVS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "IDIVS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "LTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "GTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "EQS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "ANDS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "ORS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "NOTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "INT2CHARS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "STRI2INTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "INT2FLOATS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "FLOAT2INTS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 0)
				elif xmlInstr[ind][0].upper() == "JUMPIFEQS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				elif xmlInstr[ind][0].upper() == "JUMPIFNEQS":
					self.checkArgCount(xmlInstr[ind][0] ,len(xmlInstr[ind]) -1, 1)
					self.checkLabel(xmlInstr[ind][1], -1)
				temp = [xmlInstr[order[i][0]][0], xmlInstr[order[i][0]][1:]]
				#appends instructions with arguments in the right order 
				self.instructions.append(temp)
			except IndexError:
				raise ParseError("wrong arguments for instruction '%s'" % xmlInstr[ind][0])

	#checks the correct values for variables
	# that means {FRAME}@{acceptable values for var}
	def checkVar(self, arg):
		if arg[0] != 'var' :
			raise ParseError("variable should have been 'var' not '%s'" % arg[0])
		try:
			arg = arg[1].split('@',1)
		except ValueError:
			raise ParseError("missing @ after frame")

		if arg[0] not in ['LF', 'TF', 'GF']:
			raise ParseError("wrong frame: %s" % arg[0])

		if not re.match(r"^[a-zá-žA-ZÁ-Ž_\-$&%*?!][\w\-$&%*?!]*$", arg[1]):
			raise ParseError("variable '%s' is invalid" % arg[1])

	#checks the correct values for var	
	# that means [{TYPE}, {acceptable values for symbol}]
	def checkSymb(self, arg):
		if arg[0] == 'var':
			self.checkVar(arg)
		elif arg[0] == 'nil':
			if arg[1] != 'nil':
				raise ParseError("invalid 'nil' value")
		elif arg[0] == 'int':
			try:
				arg[1] = int(arg[1])
			except (ValueError, TypeError, OverflowError):
				raise ParseError("invalid 'int' value: '%s'" % arg[1])
		elif arg[0] == 'float':
			try:
				arg[1] = float.fromhex(arg[1])
			except (ValueError, TypeError):
				raise ParseError("invalid 'float' value: '%s'" % arg[1])
		elif arg[0] == 'bool':
			if arg[1] != 'true' and arg[1] != 'false':
				raise ParseError("invalid 'bool' value: '%s'" % arg[1])
		elif arg[0] == 'string':
			if arg[1] == None:
				arg[1] = ''
			elif ('#' in arg[1] or re.search(r"\s", arg[1])):
				raise ParseError("invalid 'string' value: '%s'" % arg[1])
			else:
				for i in range(0,len(arg[1])):
					if i == len(arg[1]):	
						break;	#when there was escape sequence, it is shorter then before
					# managing escape sequences
					if arg[1][i] == '\\':
						try:
							escape = arg[1][i+1] + arg[1][i+2] + arg[1][i+3]
							escape = int(escape)
							arg[1] = arg[1][:i] + chr(escape) + arg[1][i+4:]
						except (ValueError, TypeError, IndexError):
							raise ParseError("invalid 'string' value: '%s'" % arg[1])
		else:
			raise ParseError("invalid symbol: cannot be '%s'" % arg[0])

	#checks validity and the correct vales of label in 'arg'
	#if it is called by LABEL, it will append to labels, or raise exception
	#if it is called by JUMP-like instructions it checks existence of the label in arg
	#ind is the index where the label is located, if it's -1 its not important
	def checkLabel(self, arg, ind):
		if arg[0] != 'label':
			raise ParseError("type label is needed, not '%s'" % arg[0])
		if not re.match(r"^[a-zá-žA-ZÁ-Ž_\-$&%*?!][\w\-$&%*?!]*$", arg[1]):
			raise ParseError("label '%s' is invalid" % arg[1])
		if ind != -1:	#if == -1 , that means instructions CALL JUMP etc
			if arg[1] in self.labels:
				raise SemanticsError("Redefinition of label '%s'" % arg[1])	
			else:			#this means instruction LABEL
				self.labels.append(arg[1])
				self.labelIndex.append(ind)	#saves index in the whole code, to faster execution
		
	#checks type in 'arg' for instruction READ
	def checkType(self, arg):
		if arg[0] != 'type':
			raise ParseError("arg 'type' is needed, not '%s'" % arg[0])
		if arg[1] not in ['int', 'bool', 'string', 'float']:
			raise ParseError("invalid type: '%s'" % arg[1])

	#goes to entered label and returns the index where the label is located in code)
	def goToLabel(self, label, call):
		if label not in self.labels: 
			raise SemanticsError("could not go to label '%s', it is not defined" % label)
		else: 
			if call != -1:
				self.calls.append(call) #appends position (index) where it should return
			move = self.labelIndex[self.labels.index(label)]#return the label position in code  
			return move

	# executes the instructions
	#inputFile is the input file for instruction READ
	#inputBool is True if input file is a real file, False if it is from STDIN
	def interpret(self, inputFile, inputBool):
		current = 0		#index of currently executed instruction
		while current < len(self.instructions):
			self.instrCount += 1
			if self.instructions[current][0].upper() == "MOVE":
				self.run.move(self.instructions[current][1][0][1].split('@',1),
							self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "CREATEFRAME":
				self.run.TF = [] 	#creates empty TF 
			elif self.instructions[current][0].upper() == "PUSHFRAME":
				self.run.pushFrame()
			elif self.instructions[current][0].upper() == "POPFRAME":
				self.run.popFrame()
			elif self.instructions[current][0].upper() == "DEFVAR":
				self.run.defVar(self.instructions[current][1][0][1].split('@',1), current)
			elif self.instructions[current][0].upper() == "CALL":
				current = self.goToLabel(self.instructions[current][1][0][1], current)
				self.instrCount += 1	# 'execution' of label
			elif self.instructions[current][0].upper() == "RETURN":
				if self.calls == []:
					raise MissingValue("empty CALL stack")
				else:	#changes to position where it was called
					current = self.calls.pop(-1)	
			elif self.instructions[current][0].upper() == "PUSHS":
				self.run.pushs(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "POPS":
				self.run.pops(self.instructions[current][1][0][1].split('@',1))
			elif self.instructions[current][0].upper() == "ADD":
				self.run.calculate("ADD",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "SUB":
				self.run.calculate("SUB",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "MUL":
				self.run.calculate("MUL",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "IDIV":
				self.run.calculate("IDIV",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "DIV":
				self.run.calculate("DIV",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "LT":
				self.run.conditions("LT",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "GT":
				self.run.conditions("GT",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "EQ":
				self.run.conditions("EQ",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "AND":
				self.run.logical("AND",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "OR":
				self.run.logical("OR",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "NOT":
				self.run.logical("NOT",self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "INT2CHAR":
				self.run.int2Char(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "FLOAT2INT":
				self.run.float2Int(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "INT2FLOAT":
				self.run.int2Float(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "STRI2INT":
				self.run.stri2Int(self.instructions[current][1][0][1].split('@',1),
										self.instructions[current][1][1],
										self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "READ":
				self.run.read(self.instructions[current][1][0][1].split('@',1),
							self.instructions[current][1][1][1], inputFile, inputBool)
			elif self.instructions[current][0].upper() == "WRITE":
				self.run.write(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "CONCAT":
				self.run.concat(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1],
								self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "STRLEN":
				self.run.strlen(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "GETCHAR":
				self.run.getchar(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1],
								self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "SETCHAR":
				self.run.setchar(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1],
								self.instructions[current][1][2])
			elif self.instructions[current][0].upper() == "TYPE":
				self.run.instrType(self.instructions[current][1][0][1].split('@',1),
								self.instructions[current][1][1])
			elif self.instructions[current][0].upper() == "LABEL":
				pass #did it earlier
			elif self.instructions[current][0].upper() == "JUMP":
				current = self.goToLabel(self.instructions[current][1][0][1], -1)
				self.instrCount += 1	#the 'execution' of label
			elif self.instructions[current][0].upper() == "JUMPIFEQ":
				retBool = self.run.condJumps("JUMPIFEQ", self.instructions[current][1][1],
								self.instructions[current][1][2])
				if retBool == True:	#jumps to label
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			elif self.instructions[current][0].upper() == "JUMPIFNEQ":
				retBool = self.run.condJumps("JUMPIFNEQ", self.instructions[current][1][1],
								self.instructions[current][1][2])
				if retBool == True:	#jumps to label
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			elif self.instructions[current][0].upper() == "EXIT":
				exitVal = self.run.instrExit(self.instructions[current][1][0])
				self.initVars = self.run.initializedVars	#to save stats
				return exitVal
			elif self.instructions[current][0].upper() == "DPRINT":
				self.run.dprint(self.instructions[current][1][0])
			elif self.instructions[current][0].upper() == "BREAK":
				justToBeExact = 'th'	#variable just to be English correct
				if current == 1:
					justToBeExact = 'st'
				elif current == 2:
					justToBeExact = 'nd'
				elif current == 3:
					justToBeExact = 'rd'
				sys.stderr.write(
"""Currently providing instruction:				{0}{6} instruction (out of {7})
Count of executed instructions were (this one excluded): 	{1}
Currently in data stack:	{2}
Currently in Global Frame:	{3}
Currently in Temporary Frame:	{4}
Currently in Local Frame:	{5}
""".format(current +1,self.instrCount -1, self.run.dataStack, self.run.GF, 
	self.run.TF, self.run.LF,justToBeExact,len(self.instructions)))
			elif self.instructions[current][0].upper() == "CLEARS":
				self.run.dataStack = []	#clears dataStack
			elif self.instructions[current][0].upper() == "ADDS":
				self.run.calculate("ADDS",None,None,None,True)
			elif self.instructions[current][0].upper() == "SUBS":
				self.run.calculate("SUBS",None,None,None,True)
			elif self.instructions[current][0].upper() == "MULS":
				self.run.calculate("MULS",None,None,None,True)
			elif self.instructions[current][0].upper() == "DIVS":
				self.run.calculate("DIVS",None,None,None,True)
			elif self.instructions[current][0].upper() == "IDIVS":
				self.run.calculate("IDIVS",None,None,None,True)
			elif self.instructions[current][0].upper() == "LTS":
				self.run.conditions("LT",None,None,None,True)
			elif self.instructions[current][0].upper() == "GTS":
				self.run.conditions("GT",None,None,None,True)
			elif self.instructions[current][0].upper() == "EQS":
				self.run.conditions("EQ",None,None,None,True)
			elif self.instructions[current][0].upper() == "ANDS":
				self.run.logical("AND",None,None,None,True)
			elif self.instructions[current][0].upper() == "ORS":
				self.run.logical("OR",None,None,None,True)
			elif self.instructions[current][0].upper() == "NOTS":
				self.run.logical("NOT",None,None,None,True)
			elif self.instructions[current][0].upper() == "INT2CHARS":
				self.run.int2Char(None, None, True)
			elif self.instructions[current][0].upper() == "STRI2INTS":
				self.run.stri2Int(None, None, None, True)
			elif self.instructions[current][0].upper() == "INT2FLOATS":
				self.run.int2Float(None, None, True)
			elif self.instructions[current][0].upper() == "FLOAT2INTS":
				self.run.float2Int(None, None, True)
			elif self.instructions[current][0].upper() == "JUMPIFEQS":
				retBool = self.run.condJumps("JUMPIFEQ", None, None, True)
				if retBool == True:
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			elif self.instructions[current][0].upper() == "JUMPIFNEQS":
				retBool = self.run.condJumps("JUMPIFNEQ", None, None, True)
				if retBool == True:
					current = self.goToLabel(self.instructions[current][1][0][1], -1)
					self.instrCount += 1
			current += 1
		self.initVars = self.run.initializedVars
		return True
		
'''
Classes for managing error cases with the error message
'''
class ParseError(Exception):
	pass
class SemanticsError(Exception):
	pass
class WrongArgTypes(Exception):
	pass
class UndefinedVar(Exception):
	pass
class FrameError(Exception):
	pass
class MissingValue(Exception):
	pass
class WrongValue(Exception):
	pass
class StringError(Exception):
	pass


		
			
