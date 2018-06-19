
DESTDIR =
SERVERDIR = $(DESTDIR)/var/lib/photodb
BINDIR = $(DESTDIR)/usr/bin

all:

clean:
	find . -name "*~" | xargs rm -f
	find . -name "__pycache__" | xargs rm -rf

install:
	install -d $(SERVERDIR)
	cp *.py cherryApp.conf nobody.jpg updateDb.sh haarcascade_frontalface_default.xml $(SERVERDIR)
	cp -a static templates $(SERVERDIR)
	# fix the cherrypy configuration
	sed -i 's%tools.staticdir.root.*%tools.staticdir.root = "/var/lib/photodb"%' $(SERVERDIR)/cherryApp.conf
	install -d $(BINDIR)
	cp photodbServer $(BINDIR)

.PHONY: all clean install
