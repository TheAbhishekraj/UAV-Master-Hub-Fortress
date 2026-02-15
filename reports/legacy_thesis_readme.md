# PhD Thesis LaTeX Source

**Dissertation: Autonomous Thermal-Imaging Hexacopter for Precision Agriculture**

---

## Structure

```
thesis/
├── main.tex                # Main thesis document
├── chapters/
│   ├── 01_introduction.tex
│   ├── 02_literature_review.tex
│   ├── 03_methodology.tex
│   ├── 04_system_design.tex
│   ├── 05_implementation.tex
│   ├── 06_validation.tex
│   ├── 07_results.tex
│   └── 08_conclusion.tex
├── figures/
│   ├── hexacopter_cad.png
│   ├── thermal_detection.png
│   └── mission_telemetry.png
├── references.bib          # BibTeX bibliography
└── thesis.pdf              # Compiled PDF
```

---

## Compilation

```bash
cd thesis/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use:
```bash
latexmk -pdf main.tex
```

---

**Status:** In progress  
**Target Defense Date:** [TBD]  
**Last Updated:** February 15, 2026
