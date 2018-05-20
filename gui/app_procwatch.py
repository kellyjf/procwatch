# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings-db.ui'
#
# Created: Fri May 18 08:07:40 2018
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app_dbsettings import *
from ui_procwatch import *

select="select to_char(mtime,'99999D999') as \"Boot\", etime::time as \"Time\", to_char(pid,'99999') as pid, to_char(ppid,'99999') as ppid, netns, args as \"Command\""

class Procwatch(QMainWindow, Ui_Procwatch ):
	def __init__(self,parent=None):
		super(type(self), self).__init__(parent)
		self.setupUi(self)
		self.dbsettings=DbSettings(self, QSettings("Gogo, Inc", "procwatch"))
		self.db=Database()
		self.db.connect()	

		self.connect(self.queryButton, SIGNAL("clicked()"), self.query)
		self.connect(self.action_Settings, SIGNAL("activated()"), self.dbsettings.show)
		self.connect(self.mainTable, SIGNAL("cellDoubleClicked(int, int)"), self.setpid)
	
	def query(self):
		clause=[]
		param=[]

		cmdfilt=self.filterLine.text()
		if cmdfilt:
			clause.append("\"Command\" like '%%{}%%'".format(cmdfilt))
			
		pidfilt=self.pidLine.text()
		if pidfilt:
			clause.append("\"Pid\"=%s")
			param.append(str(pidfilt))
		
		if clause:
			wsql="where "+ " and ".join(clause)
		else:
			wsql=""

		sql="select \"Boot\", \"Time\", \"Pid\", \"NetNS\", \"Command\" from commands {} order by mtime".format(wsql)
		self.mainTable.show(self.db.execute(sql,param))
			
	def setpid(self, row, col):
		item=self.mainTable.item(row,0)
		if 'userdata' in item.__dict__:
			if 'ppid' in item.userdata:
				self.siblingTable.show(self.db.execute(select+" from args where ppid=%s order by mtime", [item.userdata['ppid']]))

			if 'Pid' in item.userdata:
				#self.childrenTable.show(self.db.execute(select+" from args where ppid=%s", [item.userdata['pid']]))
#				self.childrenTable.show(self.db.execute("select mtime as \"Boot\", etime::time as \"Time\", pid, cpid from forks where pid=%s order by mtime", [item.userdata['pid']]))
				ancestors=CurList()
				pid=int(item.userdata['Pid'])
				mtime=float(item.userdata['Boot'])
				ppid=None
				pmtime=None
				while True:
					curs=self.db.execute("select \"Boot\", \"Time\", \"Pid\",\"Cpid\",\"Command\" from parents where cpid=%s and mtime-10.0<%s order by mtime desc limit 1", [pid,mtime])
					ancestors.describe(curs.description)
					if curs.rowcount==1:
						row=curs.fetchone()
						pid=int(row[2])
						mtime=float(row[0])
						if not ppid:
							ppid=pid
							pmtime=mtime
						ancestors.addrows([row])
						curs.close()
					else:
						curs.close()
						break
				self.parentTable.show(ancestors)

				self.siblingTable.show(self.db.execute("select \"Boot\", \"Time\", \"Pid\",\"Cpid\",\"Command\" from parents where pid=%s and mtime+10.0>%s order by mtime desc", [ppid,pmtime]))

				self.childrenTable.show(self.db.execute("select \"Boot\", \"Time\", \"Pid\",\"Cpid\",\"Command\" from parents where pid=%s order by mtime", [int(item.userdata['Pid'])]))


if __name__ == "__main__":
	import sys
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = QtGui.QApplication(sys.argv)
	win=Procwatch()
	win.show()
	sys.exit(app.exec_())

