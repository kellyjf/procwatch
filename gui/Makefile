

UI := ui_dbsettings.py 

all: test 

ui: $(UI)

ui_%.py : %.ui
	pyuic4 -i 0 $< > $@

clean:
	rm -f $(UI) *.pyc

test: $(UI)
	python app_dbsettings.py

help:
	echo This is Make Help
