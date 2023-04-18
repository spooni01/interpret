############################################################################
# Project: Interpret
# File: Makefile
# Author: Adam Ližičiar xlizic00@stud.fit.vutbr.cz
#
# Description: Build script
############################################################################

ZIP_FILES = classes doc interpret.py readme2.md
ZIP_NAME = xlizic00.zip


pack:
	zip -r $(ZIP_NAME) $(ZIP_FILES)