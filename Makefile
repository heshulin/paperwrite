.PHONY: pdf clean watch

pdf:
	cd paper && latexmk -pdf -outdir=build main.tex

clean:
	cd paper && latexmk -C -outdir=build main.tex

watch:
	cd paper && latexmk -pdf -pvc -outdir=build main.tex
