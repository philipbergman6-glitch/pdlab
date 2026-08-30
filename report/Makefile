# Build the report PDF: render numbers from results/canonical.json, then pandoc + tectonic.
CHAPTERS := 01_introduction.md 02_one_shot.md 03_finite.md 04_infinite.md \
            05_evolution_theory.md 06_numerics.md 07_original.md 08_conclusion.md
SRC := $(addprefix build/,00_meta.yaml $(CHAPTERS))
OUT := build/prisoners_dilemma_report.pdf

all: $(OUT)

.PHONY: all render clean

render: $(CHAPTERS) 00_meta.yaml references.bib ../results/canonical.json
	cd .. && uv run python scripts/render_report.py

$(OUT): render
	cd build && pandoc 00_meta.yaml $(CHAPTERS) \
	  --from markdown+tex_math_dollars+citations --filter pandoc-crossref --citeproc \
	  --bibliography=references.bib --csl=apa.csl \
	  --pdf-engine=tectonic --toc --toc-depth=2 --number-sections \
	  --resource-path=.:.. -o prisoners_dilemma_report.pdf 2> pandoc.log; \
	  status=$$?; cat pandoc.log; exit $$status
	@echo "wrote $(OUT)"

clean:
	rm -rf build
