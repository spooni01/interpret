import classes.ArgumentParser as ap
import classes.Parser as xmlpar
import classes.ErrorHandler as err

###
import sys
import ippcode_bank 
import xml.etree.ElementTree as elemTree
###

# Arguments
par = ap.ArgumentParser(add_help=False)
argv = par.checkArguments()

# Interpret
try:
	parser = xmlpar.Parser(argv.source)
	listOfNumbers, listofInstructions = parser.check()


	#######
	program = ippcode_bank.Interpret()
	program.checkInstr(listOfNumbers, listofInstructions) 			#checks if the instruction has correct order
	#runs the whole interpret, returns True, if everything fine or some value if instruction EXIT appears
	#this is for situation when we get STATI args but if we ended up earlier, the stats would not be printed
	exitVal = program.interpret(argv.input, par.isFile)		
	#STATI extension
	#prints wanted information to file given to sys.arg --stats
	
	if exitVal != True:	#this means that EXIT was called
		sys.exit(exitVal)

#Error messages handling with the corresponding error code 
except elemTree.ParseError as wrongxml:
	sys.stderr.write("ERROR: wrong XML format-> %s!\n" % str(wrongxml))
	sys.exit(31)
except TypeError as wrongxml:
	sys.stderr.write("ERROR: wrong XML format-> %s!\n" % str(wrongxml))
	sys.exit(32)
except FileNotFoundError:
	sys.stderr.write("ERROR: Source file cannot be opened !\n")
	sys.exit(11)
except ippcode_bank.ParseError as wrongsyntax:
	sys.stderr.write("ERROR: syntax error-> %s!\n" % str(wrongsyntax))
	sys.exit(32)
except ippcode_bank.SemanticsError as wrongsemantics:
	sys.stderr.write("ERROR: semantics error-> %s!\n" % str(wrongsemantics))
	sys.exit(52)
except ippcode_bank.WrongArgTypes as wrongargs:
	sys.stderr.write("ERROR: wrong operands type-> %s!\n" % str(wrongargs))
	sys.exit(53)
except ippcode_bank.UndefinedVar as wrongvar:
	sys.stderr.write("ERROR: variable error-> %s!\n" % str(wrongvar))
	sys.exit(54)
except ippcode_bank.FrameError as frameError:
	sys.stderr.write("ERROR: %s !\n" % str(frameError))
	sys.exit(55)
except ippcode_bank.MissingValue as missingValue:
	sys.stderr.write("ERROR: missing value-> %s!\n" % str(missingValue))
	sys.exit(56)
except ippcode_bank.WrongValue as wrongvalue:
	sys.stderr.write("ERROR: wrong value-> %s!\n" % str(wrongvalue))
	sys.exit(57)
except ippcode_bank.StringError as wrongstring:
	sys.stderr.write("ERROR: error with string-> %s!\n" % str(wrongstring))
	sys.exit(58)
