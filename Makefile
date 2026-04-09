.PHONY: pdf clean watch install

install:
	pip install -e .

pdf:
	cd paper && tectonic -o build main.tex

clean:
	rm -f paper/build/*
