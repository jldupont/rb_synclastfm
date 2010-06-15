#
# @author Jean-Lou Dupont
#
#
PRJ=rb_synclastfm

PYTHON=`which python`
RBP=/usr/lib/rhythmbox/plugins

all:
	@echo "make install"
	@echo "make clean"
	@echo "make buildsrc"

clean:
	@rm -f $(DESTDIR)$(RBP)/synclastfm/*.pyc
		
install:
	@install -d $(DESTDIR)$(RBP)/synclastfm
	@install -d $(DESTDIR)$(RBP)/synclastfm/agents
	@install -d $(DESTDIR)$(RBP)/synclastfm/system
	
	@install -D $(CURDIR)/synclastfm/*.py                  $(DESTDIR)$(RBP)/synclastfm/
	@install -D $(CURDIR)/synclastfm/agents/*.py           $(DESTDIR)$(RBP)/synclastfm/agents
	@install -D $(CURDIR)/synclastfm/system/*.py           $(DESTDIR)$(RBP)/synclastfm/system
	
	@install -D $(CURDIR)/synclastfm/*.glade               $(DESTDIR)$(RBP)/synclastfm/	
	@install -D $(CURDIR)/synclastfm/synclastfm.rb-plugin  $(DESTDIR)$(RBP)/synclastfm/synclastfm.rb-plugin
	@python -m compileall ${DESTDIR}$(RBP)/synclastfm
	
buildsrc:
	debuild -S