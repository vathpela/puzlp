TESTS=pmj-themeless-zero.puz solve-for-x.puz

all:

test:
	export PPD=$$PWD/manufacturing.ppd ; \
	export PRINTER=ignore ; \
	export CLASS=ignore ; \
	export CUPS_CACHEDIR="" ; \
	export CUPS_DATADIR="" ; \
	export CUPS_SERVERROOT="" ; \
	export DEVICE_URI="" ; \
	export CONTENT_TYPE="application/x-crossword" ; \
	for test in $(TESTS) ; do \
		./puzlp 1 pjones $${test} 1 "" data/$${test} > $${test%%.puz}.pdf ; \
	done

clean:
	@rm -vf *.pdf
