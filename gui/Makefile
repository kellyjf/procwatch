

UI := ui_settingsdb.py 

all: test 

ui: $(UI)

ui_%.py : %.ui
	pyuic4 -i 0 $< > $@

clean:
	rm -f $(UI) *.pyc

test: $(UI)
	python app_settingsdb.py

help:
	echo This is Make Help
