.PHONY: pdf clean watch

pdf:
	cd paper && conda run -n paperwrite tectonic -o build main.tex

clean:
	rm -f paper/build/*

watch:
	cd paper && conda run -n paperwrite tectonic -o build --watch main.tex
