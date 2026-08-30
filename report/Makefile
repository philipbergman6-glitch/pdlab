# Build the report PDF with pandoc + tectonic.
SRC := 00_meta.yaml 01_introduction.md 02_one_shot.md 03_finite.md 04_infinite.md \
       05_evolution_theory.md 06_numerics.md 07_original.md 08_conclusion.md
OUT := build/prisoners_dilemma_report.pdf

all: $(OUT)

$(OUT): $(SRC) references.bib
	mkdir -p build
	pandoc $(SRC) --from markdown+tex_math_dollars+citations --citeproc \
	  --bibliography=references.bib --csl=apa.csl \
	  --pdf-engine=tectonic --toc --toc-depth=2 -o $(OUT) 2> build/pandoc.log
	@echo "wrote $(OUT)"; cat build/pandoc.log

clean:
	rm -rf build
