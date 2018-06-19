
DESTDIR =

all:

clean:
	find . -name "*~" | xargs rm -f
	find . -name "__pycache__" | xargs rm -rf

install:

.PHONY: all clean install
