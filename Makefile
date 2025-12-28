LATEXCMD = lualatex -shell-escape -output-directory build/
TEXINPUTS := .:library/tex:
export TEXINPUTS
export max_print_line := 1048576

.PHONY: help kit clean
build:
	mkdir -p build

help:
	@echo "This makefile builds mvb-kit"
	@echo ""
	@echo "Available commands:"
	@echo "  make kit   - build KIT"

kit: build
	$(LATEXCMD) library/mvbkit.tex
	$(LATEXCMD) library/mvbkit.tex
	rm -f header.tmp

clean:
	rm -rf build

