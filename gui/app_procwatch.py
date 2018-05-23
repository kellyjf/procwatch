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
import pytz
import fload

select="select to_char(mtime,'99999D999') as \"Boot\", etime::time as \"Time\", to_char(pid,'99999') as pid, to_char(ppid,'99999') as ppid, netns, args as \"Command\""

class Procwatch(QMainWindow, Ui_Procwatch ):
	def __init__(self,parent=None):
		super(type(self), self).__init__(parent)
		self.setupUi(self)
		self.dbsettings=DbSettings(self, QSettings("Gogo, Inc", "procwatch"))
		self.db=Database()
		self.db.connect()	
		self.db.dictlist("set timezone=\"UTC\"")

		
		self.connect(self.clearButton, SIGNAL("clicked()"), self.clear)
		self.connect(self.queryButton, SIGNAL("clicked()"), self.query)
		self.connect(self.action_Settings, SIGNAL("activated()"), self.dbsettings.show)
		self.connect(self.action_Init, SIGNAL("activated()"), self.initdb)
		self.connect(self.action_Load, SIGNAL("activated()"), self.load)
		self.connect(self.mainTable, SIGNAL("cellDoubleClicked(int, int)"), self.setpid)
		self.connect(self.parentTable, SIGNAL("cellDoubleClicked(int, int)"), self.parentpid)

		self.metadata()
		self.clear()
	
	def metadata(self):
		self.timebox=self.db.dictlist("select min(mtime) as mmin, min(etime) at time zone 'UTC'  as emin, max(mtime) as mmax, max(etime) at time zone 'UTC'  as emax from args")[0]
		self.nslist=self.db.dictlist("select netns, count(netns) as pop  from args group by 1 order by 1")
		self.netnsCombo.clear()
		self.netnsCombo.insertItem(0, "")
		self.netnsCombo.insertItems(1,[ "{0} {1:5d}".format(x.get('netns'),x.get('pop')) for x in self.nslist])
		self.clear()

	def initdb(self):
		self.db.close()
		dbname=self.dbsettings.get("database")
		fload.initdb(dbname)
		self.db.connect()

	def load(self):
		dbname=self.dbsettings.get("database")
		flist=[str(x) for x in QFileDialog.getOpenFileNames()]
		fload.loadfiles(dbname,flist)
		self.metadata()

	def clear(self):
		if self.timebox.get('emin'):
			print self.timebox

			self.sinceTime.setDateTime(self.timebox.get('emin'))
			self.untilTime.setDateTime(self.timebox.get('emax'))

			self.sinceTime.setMinimumDateTime(self.timebox.get('emin'))
			self.sinceTime.setMaximumDateTime(self.timebox.get('emax'))
			self.untilTime.setMinimumDateTime(self.timebox.get('emin'))
			self.untilTime.setMaximumDateTime(self.timebox.get('emax'))

			self.netnsCombo.setCurrentIndex(0)
		self.filterLine.setText("")
		self.pidLine.setText("")

	def query(self):
		clause=[]
		param=[]

		clause.append("etime between %s and %s")
		param.extend([
			pytz.utc.localize(self.sinceTime.dateTime().toPyDateTime()),
			pytz.utc.localize(self.untilTime.dateTime().toPyDateTime())])

		nsfilt=str(self.netnsCombo.currentText())
		if nsfilt:
			ns,_ = nsfilt.split()
			clause.append("\"NetNS\"=%s")
			param.append(ns)

		cmdfilt=self.filterLine.text()
		if cmdfilt:
			clause.append("\"Command\" like '%%{}%%'".format(cmdfilt))
			
		pidfilt=self.pidLine.text()
		if pidfilt:
			clause.append("pid=%s")
			param.append(str(pidfilt))
		
		if clause:
			wsql="where "+ " and ".join(clause)
		else:
			wsql=""

		sql="select \"Boot\", \"Time\", \"Pid\", \"NetNS\", \"Command\" from commands {} order by mtime".format(wsql)
		self.mainTable.show(self.db.execute(sql,param))
			
	def nearby(self, mtime):
		sql="select \"Boot\", \"Time\", \"Pid\", \"NetNS\", \"Command\" from commands where abs(mtime-%s)<2 order by mtime"
		self.mainTable.show(self.db.execute(sql,[float(mtime)]))

	def parentpid(self, row, col):
		item=self.parentTable.item(row,0)
		if 'userdata' in item.__dict__:
			if 'Boot' in item.userdata:
				self.nearby(item.userdata['Boot'])
			for row in range(self.mainTable.rowCount()):
				pitem=self.mainTable.item(row,0)
				pdata=pitem.userdata
				if pitem.userdata['Pid']==item.userdata['Pid']:
					self.mainTable.setCurrentCell(row,0)
					self.mainTable.setCurrentItem(pitem)
					self.mainTable.scrollToItem(pitem)
					break
		
	def setpid(self, row, col):
		item=self.mainTable.item(row,0)
		self.parentTable.clear()
		self.siblingTable.clear()
		self.childrenTable.clear()
		if 'userdata' in item.__dict__:
			if 'Pid' in item.userdata:
				pid=int(item.userdata['Pid'])
				mtime=float(item.userdata['Boot'])
				ppid=None
				pmtime=None

				ancestors=CurList()
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

