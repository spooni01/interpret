############################################################################
# Project: Interpret
# File: Makefile
# Author: Adam Ližičiar xlizic00@stud.fit.vutbr.cz
#
# Description: Build script
############################################################################
ZIP_FILES = classes interpret.py readme2.md 	# Define the files to include in the zip file
ZIP_NAME = 	xlizic00.zip 						# Define the name of the zip file
TMP_DIR = tmpdir


.PHONY: clean testInterpret is_it_ok pack

clean:
	del -f *.exe *.out *.core *.zip
	rmdir /s /q __pycache__
	rmdir /s /q classes/__pycache__

test:
	mkdir tmpdir
	rmdir tmpdir

testInterpret:
	sh .\tests\tests_interpret\test.sh

is_it_ok:
	.\is_it_ok.sh $(ZIP_NAME) $(TMP_DIR)
	rmdir tmpdir

pack:
	zip -r $(ZIP_NAME) $(ZIP_FILES)
