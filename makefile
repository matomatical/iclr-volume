%.png: %.pdf
	mutool draw -w 1500 -o $@ $<

%.svg: %.pdf
	mutool draw -o $@ $<

download:
	python main.py download

timeline.pdf: main.py iclr2025.pickle
	python main.py timeline

wordcounts.pdf: main.py iclr2025.pickle
	python main.py wordcount


.PHONY: download


	

