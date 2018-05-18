# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings-db.ui'
#
# Created: Fri May 18 08:07:40 2018
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from  ui_settingsdb import *

class SettingsDbFrame(QFrame, Ui_SettingsDbFrame):
	def __init__(self,parent=None):
		super(QFrame, self).__init__(parent)
		self.setupUi(self)

if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	dlg=QMainWindow()
	win=SettingsDbFrame(dlg)
	dlg.show()
	sys.exit(app.exec_())

