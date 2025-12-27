LATEXCMD = lualatex -shell-escape -output-directory build/
export TEXINPUTS=.:library/tex/:
export max_print_line = 1048576

help:
	@echo "This makefile builds mvb-kit"
	@echo ""
	@echo "Available commands are:"
	@echo "	make ubtl		- to build KACTL"
	@echo "	make clean		- to clean up the build process"
	@echo "	make veryclean		- to clean up and remove kactl.pdf"
	@echo "	make test		- to run all the stress tests in stress-tests/"
	@echo "	make test-compiles	- to test compiling all headers"
	@echo "	make help		- to show this information"
	@echo "	make showexcluded	- to show files that are not included in the doc"
	@echo ""
	@echo "For more information see the file 'doc/README'"

