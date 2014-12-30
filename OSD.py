# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import os, math, urllib, time, Kartina
import urllib2

pausedelay = 0
archivePlayBuffer = 0

delayTimer = QtCore.QTimer()
delayTimer.setInterval(1000)

def convertTime(uxtime):
    return time.strftime("%H:%M", time.localtime(int(uxtime) + Kartina.timeshift))

class OSD(QtGui.QWidget):
    def __init__(self, parent):
        super(OSD, self).__init__(parent)
        self.parent = parent
        
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        
        self.hEntry = 0
        self.fontDivider = 50
        
        self.visible = False
        
    @classmethod
    def postInit(self, obj, videoarea):
        ### set OSD Size        
        obj.setSize(videoarea)
        obj.setFontSize()
        
        ### Visibility
        obj.doHide()
        
    def isVisible(self):
        return self.visible
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()
        self.setSize(self.parent.Video.getGeometry())
        
    def drawWidget(self, qp):
        color = QtGui.QColor(0, 0, 0)
        
        color.setNamedColor('#000000')
        qp.setPen(color)
        qp.setBrush(QtGui.QColor(17, 17, 17))
        qp.drawRect(0, 0, self.w, self.h)
        
    def setSize(self, videoarea, OSDType = None):
        x = videoarea.x()
        y = videoarea.y()
        w = videoarea.width()
        h = videoarea.height()
        if x != self.x or y != self.y or w != self.w or h != self.h:
            if OSDType == "ChannelList":
                self.x = math.floor(x + w*10/100)        
                self.y = math.floor(y + h*5/100)
                self.w = math.floor((w - 2*w*10/100) / 2)
                self.hEntry = math.floor(h*(100-2*5)/100/11/2)
                self.h = self.hEntry * 11
            elif OSDType == "EPG":
                self.x = math.floor(x + w*10/100)        
                self.y = math.floor(y + h*5/100)
                self.w = math.floor((w - 2*w*10/100))
                self.hEntry = math.floor(h*(100-2*5)/100/7)
                self.h = self.hEntry * 6 + math.floor(self.hEntry/2)
            elif OSDType == "Info":
                self.x = math.floor(x + w*10/100)        
                self.y = math.floor(y + h*60/100)
                self.w = w - 2*w*10/100
                self.hEntry = math.floor((h*35/100)/2.5)
                self.h = math.floor(self.hEntry*2.5)
            elif OSDType == "MoreInfo":    
                self.x = math.floor(x + w*10/100)        
                self.y = math.floor(y + h*5/100)
                self.w = math.floor(w - 2*w*10/100)
                self.h = math.floor(h*90/100)
            elif OSDType == "Notify":    
                self.x = math.floor(x + w*75/100)        
                self.y = math.floor(y + h*5/100)
                self.w = math.floor(w - 80*w/100)
                self.h = math.floor(h*7/100)
            elif OSDType == "ShutDown":    
                self.x = math.floor(x + w*25/100)        
                self.y = math.floor(y + h*30/100)
                self.w = math.floor(w - 50*w/100)
                self.hEntry = math.floor((h*40/100)/3.5)
                self.h = math.floor(self.hEntry*3.5)
            self.setFontSize()
            self.setGeometry(self.x, self.y, self.w+1, self.h+1)            

    def setFontSize(self):
        self.fontsize = str(int(math.floor(self.h / self.fontDivider)))
        
    def setFontDivider(self, value):
        self.fontDivider = value
        
    def toggleVisible(self):
        if self.visible == True:
            self.doHide()
        else:
            self.doShow()
            
    def doHide(self):
        self.visible = False
        self.hide()
    
    def doShow(self):
        self.visible = True
        self.show()
        self.showContent()
        
    def showContent(self):
        pass

class OSDList(OSD):
    def __init__(self, videoarea, parent):
        OSD.__init__(self, parent)
        
        ### Variables
        self.typeOfList = "List"
        self.nrOfEntrys = 0
        
        self.currentEntry = 0
        self.entryCount = 0
        self.listOfEntrys = []
        self.listOfContent = []
        self.position = Kartina.getTime()
            
    def goDown(self):
        if self.currentEntry + 1 < self.entryCount:
            self.currentEntry = self.currentEntry + 1
            self.showContent()
                        
    def goUp(self):
        if self.currentEntry > 0:
            self.currentEntry = self.currentEntry - 1
            self.showContent()
            
    def nextList(self):
        self.showContent()
        
    def prevList(self):
        self.showContent()
        
    def activateEntry(self):
        self.parent.Video.Info.doHide()
        self.parent.Video.currentChannelID = self.parent.Video.Clist.listOfContent[self.parent.Video.Clist.currentEntry]
        self.parent.Video.titlePosition = self.position
        self.parent.Video.loadStream(self.position, True)
        self.doHide()
        
    def resetEntrys(self):
        for i in self.listOfEntrys:
            i.setText("")
        self.currentEntry = 0
        self.listOfContent = []
        
    def setSize(self, videoarea):
        OSD.setSize(self, videoarea, self.typeOfList)
        if self.typeOfList == "EPG" or self.typeOfList == "ShutDown":
            self.lTitle.setFixedHeight(self.hEntry/2)
        else:
            self.lTitle.setFixedHeight(self.hEntry)
        for e in self.listOfEntrys:
            e.setFixedHeight(self.hEntry)
            
    def highlightEntry(self, entry, color = "#4fba40"):
        for i in self.listOfEntrys:
            if i.styleSheet() == "background-color: " + color + ";":
                i.setStyleSheet("")
        self.listOfEntrys[entry].setStyleSheet("background-color: " + color + ";")
        
    def unHighlightEntry(self, entry):
        self.listOfEntrys[entry].setStyleSheet("")
        
    def showContent(self, array):
        i = 0
        j = 0
        start = self.currentEntry - (self.nrOfEntrys - 1)
        if start < 0:
            start = 0
        for item in array[1:]:
            if j >= start:
                if i <= self.nrOfEntrys - 1:
                    self.applyContent(i, start, item)
                if i == self.nrOfEntrys - 1:
                    self.lastEntry = j
                i = i + 1
            j = j + 1
        self.entryCount = j
        OSD.showContent(self)

    def applyContent(self, i, start, item):
        pass
        
class OSDEPG(OSDList):
    def __init__(self, videoarea, parent):
        OSDList.__init__(self, videoarea, parent)
        
        ### Variables
        self.currentDay = time.strftime("%d%m%y", time.localtime(Kartina.getTime()))
        self.playDay = time.strftime("%d%m%y", time.localtime(Kartina.getTime()))
        
        ### Layout
        self.lTitle = QtGui.QLabel(self)
        self.lHelp = QtGui.QLabel(self)
        self.lProg1 = QtGui.QLabel(self)
        self.lProg2 = QtGui.QLabel(self)
        self.lProg3 = QtGui.QLabel(self)
        self.lProg4 = QtGui.QLabel(self)
        self.lProg5 = QtGui.QLabel(self)
        self.lProg6 = QtGui.QLabel(self)
        
        self.listOfEntrys.append(self.lProg1)
        self.listOfEntrys.append(self.lProg2)
        self.listOfEntrys.append(self.lProg3)
        self.listOfEntrys.append(self.lProg4)
        self.listOfEntrys.append(self.lProg5)
        self.listOfEntrys.append(self.lProg6)
        
        hBox = QtGui.QHBoxLayout()
        hBox.setContentsMargins(0, 0, 0, 0)
        hBox.setSpacing(0)
        hBox.addWidget(self.lTitle, 1)
        hBox.addWidget(self.lHelp, 0)
        
        channelVBox = QtGui.QVBoxLayout(self)
        channelVBox.addLayout(hBox, 0)
        channelVBox.addWidget(self.lProg1, 1)
        channelVBox.addWidget(self.lProg2, 1)
        channelVBox.addWidget(self.lProg3, 1)
        channelVBox.addWidget(self.lProg4, 1)
        channelVBox.addWidget(self.lProg5, 1)
        channelVBox.addWidget(self.lProg6, 1)
        channelVBox.setContentsMargins(0, 0, 0, 0)
        channelVBox.setSpacing(0)
        
        ### Class Settings
        self.typeOfList = "EPG"
        self.nrOfEntrys = 6
        self.setFontDivider(25)        
        
        ### Class postInit
        OSDList.postInit(self, videoarea)
        
    def nextList(self):
        if time.mktime(time.strptime(self.currentDay, "%d%m%y")) < Kartina.getTime() - 24 * 3600:
            newday = time.mktime(time.strptime(self.currentDay, "%d%m%y")) + 24 * 3600
            self.currentDay = time.strftime("%d%m%y", time.localtime(newday))
            self.resetEntrys()
            OSDList.nextList(self)
            
    def prevList(self):
        if time.mktime(time.strptime(self.currentDay, "%d%m%y")) > Kartina.getTime() - 24 * 3600 * 14:
            newday = time.mktime(time.strptime(self.currentDay, "%d%m%y")) - 24 * 3600
            self.currentDay = time.strftime("%d%m%y", time.localtime(newday))
            self.resetEntrys()
            OSDList.prevList(self)  
        
    def activateEntry(self):
        OSDList.activateEntry(self)
        self.playDay = self.currentDay
        self.parent.Video.setMode("archive")           
        
    def getEPGList(self):
        epglist = [[self.currentDay, self.parent.Video.Clist.currentEntry]]
        dom = Kartina.interface.getEPGDOM(self.parent.Video.currentChannelID, self.currentDay)
        for e in dom.firstChild.childNodes:
            if e.nodeName == "epg":
                for epg in e.childNodes:
                    if epg.nodeName == "item":
                        for item in epg.childNodes:
                            if item.nodeName == "ut_start":
                                    start = item.firstChild.data
                            if item.nodeName == "progname":
                                    name = item.firstChild.data
                    epglist.append([start, name])
        return epglist
        
    def doShow(self):
        OSD.doShow(self)
        self.parent.Video.Info.doHide()
        
    def showContent(self):
        if self.listOfContent == [] or self.listOfContent[0] != [self.currentDay, self.parent.Video.Clist.currentEntry]:
            self.listOfContent = self.getEPGList()

        self.lTitle.setStyleSheet("background-color: #419934;")
        self.lTitle.setText("<font style='color: #000000; font-size: " + self.fontsize + "px'><b>&nbsp;" + time.strftime("%a, %d %b %Y", time.strptime(self.currentDay, "%d%m%y")) + "</b></font>")
        #helpfont = str(math.floor((int(self.fontsize)*7)/10))
        self.lHelp.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;<font style='color: #FF0000;'><b>⚫</b></font> Schließen&nbsp;</font>")
        OSDList.showContent(self, self.listOfContent)
    
    def applyContent(self, i, start, item):
        if item[0] == self.parent.Video.Info.ctime:
            self.highlightEntry(i, "#334C25")
        else:
            self.unHighlightEntry(i)
        if self.currentEntry == i + start:
            self.highlightEntry(i)
            self.position = item[0]
            self.parent.Video.MoreInfo.textInfo = item[1]
        if int(item[0]) <= Kartina.getTime() and Kartina.Channel.getByID(Kartina.interface, self.parent.Video.Clist.listOfContent[self.parent.Video.Clist.currentEntry]).getArchive():
            play = "<font style='color: #27C8FF'>▶</font>"
        else:
            play = ""     
        self.listOfEntrys[i].setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;<b><font style='color: #000000; background-color: #FFFFFF;'>&nbsp;" + convertTime(item[0]) + "&nbsp;</font> " + play + " " + item[1] + "</b></font>")

class OSDChannelList(OSDList):
    def __init__(self, videoarea, parent):
        OSDList.__init__(self, videoarea, parent)
        
        ### Variables
        self.currentGroup = 0
        self.listOfContent = []
        
        ### Layout
        self.lTitle = QtGui.QLabel(self)
        self.lHelp = QtGui.QLabel(self)
        self.lChannel1 = QtGui.QLabel(self)
        self.lChannel2 = QtGui.QLabel(self)
        self.lChannel3 = QtGui.QLabel(self)
        self.lChannel4 = QtGui.QLabel(self)
        self.lChannel5 = QtGui.QLabel(self)
        self.lChannel6 = QtGui.QLabel(self)
        self.lChannel7 = QtGui.QLabel(self)
        self.lChannel8 = QtGui.QLabel(self)
        self.lChannel9 = QtGui.QLabel(self)
        self.lChannel10 = QtGui.QLabel(self)
        
        self.listOfEntrys.append(self.lChannel1)
        self.listOfEntrys.append(self.lChannel2)
        self.listOfEntrys.append(self.lChannel3)
        self.listOfEntrys.append(self.lChannel4)
        self.listOfEntrys.append(self.lChannel5)
        self.listOfEntrys.append(self.lChannel6)
        self.listOfEntrys.append(self.lChannel7)
        self.listOfEntrys.append(self.lChannel8)
        self.listOfEntrys.append(self.lChannel9)
        self.listOfEntrys.append(self.lChannel10)
        
        hBox = QtGui.QHBoxLayout()
        hBox.setContentsMargins(0, 0, 0, 0)
        hBox.setSpacing(0)
        hBox.addWidget(self.lTitle, 1)
        hBox.addWidget(self.lHelp, 0)
        
        channelVBox = QtGui.QVBoxLayout(self)
        channelVBox.addLayout(hBox)
        channelVBox.addWidget(self.lChannel1)
        channelVBox.addWidget(self.lChannel2)
        channelVBox.addWidget(self.lChannel3)
        channelVBox.addWidget(self.lChannel4)
        channelVBox.addWidget(self.lChannel5)
        channelVBox.addWidget(self.lChannel6)
        channelVBox.addWidget(self.lChannel7)
        channelVBox.addWidget(self.lChannel8)
        channelVBox.addWidget(self.lChannel9)
        channelVBox.addWidget(self.lChannel10)
        channelVBox.setContentsMargins(0, 0, 0, 0)
        channelVBox.setSpacing(0)
        
        ### Class Settings
        self.typeOfList = "ChannelList"
        self.nrOfEntrys = 10
        self.setFontDivider(15)        
        
        ### Class postInit
        OSDList.postInit(self, videoarea)
        
    def startEPG(self):
        self.doHide()
        self.parent.Video.currentChannelID = self.listOfContent[self.currentEntry]
        self.parent.Video.EPG.resetEntrys()
        self.parent.Video.EPG.doShow()
        
    def nextList(self):
        if self.currentGroup < len(Kartina.interface.channelList.getGroups()) - 1:
            self.currentGroup = self.currentGroup + 1
        else:
            self.currentGroup = 0
        self.resetEntrys()
        OSDList.nextList(self)
            
    def prevList(self):
        if self.currentGroup > 0:
            self.currentGroup = self.currentGroup - 1
        else:
            self.currentGroup = len(Kartina.interface.channelList.getGroups()) - 1
        self.resetEntrys()
        OSDList.prevList(self)
        
    def activateEntry(self):
        OSDList.activateEntry(self)        
        self.parent.Video.setMode("normal")
    
    def showContent(self):
        group = Kartina.interface.channelList.getGroups()[self.currentGroup]
        self.cList = group.getChannels()
        self.lTitle.setStyleSheet("background-color: " + group.getColor() + ";")
        self.lTitle.setText("<font style='color: #000000; font-size: " + self.fontsize + "px'><b>&nbsp;" + group.getName() + "</b></font>")
        #helpfont = str(math.floor((int(self.fontsize)*9)/10))
        self.lHelp.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;<font style='color: #FF0000;'><b>⚫</b></font> EPG&nbsp;</font>")
        OSDList.showContent(self, self.cList)
    
    def applyContent(self, i, start, item):
        if not item.getID() in self.listOfContent:
            self.listOfContent.append(item.getID())
        if self.listOfContent[i+start] == self.parent.Video.currentChannelID:
            self.highlightEntry(i, "#334C25")
        else:
            self.unHighlightEntry(i)
        if self.currentEntry == i + start:
            self.highlightEntry(i)
        self.listOfEntrys[i].setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'><b>&nbsp;" + item.getName() + "</b></font>")
        
        
class OSDInfo(OSD):
    def __init__(self, videoarea, parent):
        OSD.__init__(self, parent)
        
        ### Variables
        self.ctime = None
        self.cprog = None
        self.cntime = None
        self.cnprog = None
        self.cicon = None
        self.iconPixmap = None
        
        ### Layout
        self.lprog = QtGui.QLabel(self)
        self.lnprog = QtGui.QLabel(self)
        self.lIcon = QtGui.QLabel(self)
        self.lcNr = QtGui.QLabel(self)
        self.lChannel = QtGui.QLabel(self)
        self.lHelp = QtGui.QLabel(self)
        
        self.lChannel.setStyleSheet("background-color: #419934;")
        self.lIcon.setStyleSheet("background-color: #419934;")
        self.lcNr.setStyleSheet("background-color: #419934;")
        self.lcNr.setAlignment(QtCore.Qt.AlignCenter)
        
        titleBox = QtGui.QHBoxLayout()
        titleBox.addWidget(self.lChannel, 1)
        titleBox.addWidget(self.lHelp, 0)
        titleBox.setSpacing(0)
        titleBox.setContentsMargins(0, 0, 0, 0)
        
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.lIcon, 0)
        vbox1.addWidget(self.lcNr, 1)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)
        
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addLayout(titleBox, 0)
        vbox2.addWidget(self.lprog, 1)
        vbox2.addWidget(self.lnprog, 1)   
        vbox2.setSpacing(0)
        vbox2.setContentsMargins(0, 0, 0, 0)
        
        self.hbox = QtGui.QHBoxLayout(self)
        self.hbox.addLayout(vbox1, 0)
        self.hbox.addLayout(vbox2, 1)
        self.hbox.setSpacing(0)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        
        ### set Timer for OSD Display
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(5000)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.doHide)
        
        ### Class Settings
        self.setFontDivider(7)        
        
        ### Class postInit
        OSD.postInit(self, videoarea)
        
    def setSize(self, videoarea):
        OSD.setSize(self, videoarea, "Info")
        self.lprog.setFixedHeight(self.hEntry)
        self.lnprog.setFixedHeight(self.hEntry)
        self.lHelp.setFixedHeight(math.floor(self.hEntry/2))
        self.lChannel.setFixedHeight(math.floor(self.hEntry/2))
        
    def refresh(self):
        self.ctime = None
        self.cprog = None
        self.cntime = None
        self.cnprog = None
        self.cicon = None
        self.iconPixmap = None
            
    def doHide(self):
        OSD.doHide(self)
        self.timer.stop()
    
    def doShow(self):
        self.refresh()
        OSD.doShow(self)
        self.timer.start()
            
    def filterNameFromEPG(self, epgstring):
        if '"' in epgstring:
            temp = ""
            fc = False
            for c in epgstring:
                if c != '"' and not fc:
                    pass
                elif c == '"' and not fc:
                    fc = True
                elif c != '"' and fc:
                    temp = temp + c
                elif c == '"' and fc:
                    break
            return temp
        else:
            return epgstring
            
    def getProgramsFromEPG(self, epg):
        for item in epg:
            if item != None and len(item) != 6:
                if int(item[0]) <= Kartina.getTime():
                    self.ctime = item[0]
                    self.parent.Video.MoreInfo.textInfo = item[1]
                    self.cprog = self.filterNameFromEPG(item[1])                        
                else:
                    self.cntime = item[0]
                    self.cnprog = self.filterNameFromEPG(item[1])
                    break
        
    def showContent(self):
        channel = Kartina.Channel.getByID(Kartina.interface, self.parent.Video.currentChannelID)
        self.cicon = channel.getIcon()
        if not self.parent.Video.playingArchive:
            channel.fillEPG(time.strftime("%d%m%y", time.localtime(Kartina.getTime())))
            self.getProgramsFromEPG(channel.getEPG())
            if self.ctime == None:
                channel.fillEPG(time.strftime("%d%m%y", time.localtime(Kartina.getTime()+24*3600)))
                self.getProgramsFromEPG(channel.getEPG())
                if self.ctime == None:
                    self.ctime = Kartina.getTime()
                    self.cprog = "- Nicht verfügbar -"
                if self.cntime == None:
                    self.cntime = Kartina.getTime()
                    self.cnprog = "- Nicht verfügbar -"
            if self.cntime == None:
                self.cntime = Kartina.getTime()
                self.cnprog = "- Nicht verfügbar -"
        else:
            channel.fillEPG(self.parent.Video.EPG.playDay)
            setbreak = False
            for item in channel.getEPG():
                if item != None and len(item) != 6:
                    if setbreak:
                        self.cntime = item[0]
                        break                                       
                    elif item[0] == self.parent.Video.titlePosition:
                        self.ctime = item[0]
                        self.cprog = self.filterNameFromEPG(item[1])
                        setbreak = True
        self.setText(self.ctime, self.cprog, self.cntime, self.cnprog, self.parent.Video.currentChannelID)
        self.setIcon()
        OSD.showContent(self)
        
    def getIcon(self):
        if self.cicon != None:
            opener = urllib2.build_opener()
            try:
                url = opener.open('http://iptv.kartina.tv' + self.cicon)
            except urllib.error.URLError:
                return QtGui.QPixmap("nopic.png")
            data = url.read()
            img = QtGui.QImage.fromData(data)
            pixmap = QtGui.QPixmap.fromImage(img)
            return pixmap
        else:
            return QtGui.QPixmap("nopic.png")       
        
    def setIcon(self):
        self.iconPixmap = self.getIcon()
        self.lIcon.setPixmap(self.iconPixmap.scaledToWidth((self.w/100)*10, QtCore.Qt.SmoothTransformation))
                
    def setText(self, ctime, cprog, cntime, cnprog, cNr):
        helpfont = str(math.floor((int(self.fontsize)*7)/10))
        self.lChannel.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;" + Kartina.Channel.getByID(Kartina.interface, self.parent.Video.currentChannelID).getName() + "</font>")
        self.lHelp.setText("<font style='color: #FFFFFF; font-size: " + helpfont + "px'>&nbsp;<font style='color: #FF0000;'><b>⚫</b></font> PRG <font style='color: #00FF00;'><b>⚫</b></font> EPG&nbsp;</font>")
        self.lcNr.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>" + "#" + cNr + "</font>")
        if cnprog != None and pausedelay != 0:
            if pausedelay < 0:
                prefix = "+"
            else:
                prefix = ""
            textDelay = " <font style='color: #FF0000; font-size:" + helpfont + "px'>" + prefix + str(math.floor(-1 * pausedelay/60)) + "</font>"
        else:
            textDelay = ""
        self.lprog.setText("<font style='color: white; font-size: " + self.fontsize + "px'>&nbsp;<font style='background-color: white; color: black;'>&nbsp;" + convertTime(ctime) + textDelay + "&nbsp;</font> " + cprog + "</font>")
        if cnprog != None:
            self.lnprog.setText("<font style='color: white; font-size: " + self.fontsize + "px'>&nbsp;<font style='background-color: white; color: black;'>&nbsp;" + convertTime(cntime) + textDelay + "&nbsp;</font> " + cnprog + "</font>")
        else:            
            length = int(cntime) - int(ctime)
            pc = (self.parent.Video.playTimeBuffer + archivePlayBuffer - pausedelay) * 100 / length
            if pc < 0:
                pc = 0        
            dots = int(round(pc / (100/28)))
            if dots > 28:
                dots = 28
            if self.parent.Video.playTimeBuffer + archivePlayBuffer - pausedelay < length:
                dottext = "<font style='color: #FFFFFF;'>"            
                for i in range(dots):
                    dottext = dottext + "⚫"
                dottext = dottext + "</font><font style='color: #000000;'>"
                for i in range(28-dots):
                    dottext = dottext + "⚫"
                dottext = dottext + "</font>"
            else:
                dottext = "<font style='color: #CD0D0D;'>⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫</font>"
            
            playedMin = math.floor((self.parent.Video.playTimeBuffer + archivePlayBuffer - pausedelay) / 60)
            playedSec = (self.parent.Video.playTimeBuffer + archivePlayBuffer - pausedelay) - playedMin*60
            if playedMin < 0 or playedSec < 0:
                playedMin = 0
                playedSec = 0
            
            if playedMin < 10:
                playString = "<font style='color: #000000;'>00</font>" + str(playedMin) + ":"
            elif playedMin < 100:
                playString = "<font style='color: #000000;'>0</font>" + str(playedMin) + ":"           
            if playedSec < 10:
                playString = playString + "0" + str(playedSec)
            else:
                playString = playString + str(playedSec)
                
            self.lnprog.setText("<font style='color: white;'>&nbsp;<font style='font-size: " + helpfont + "px'>" + playString + "</font>&nbsp;<font style='font-size: " + self.fontsize + "px'>" + dottext + "</font></font>")
        

class OSDMoreInfo(OSD):
    def __init__(self, videoarea, parent):
        OSD.__init__(self, parent)
        
        ### Layout        
        self.lTitle = QtGui.QLabel(self)
        self.lInfo = QtGui.QLabel(self)        
        self.lTitle.setStyleSheet("background-color: #419934;")
        self.lInfo.setAlignment(QtCore.Qt.AlignJustify)
        self.lInfo.setWordWrap(True)
        
        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.lTitle, 0)
        self.vbox.addWidget(self.lInfo, 1)
        self.vbox.setSpacing(0)
        
        ### Class Settings
        self.setFontDivider(15)        
        
        ### Class postInit
        OSD.postInit(self, videoarea)
        
    def setSize(self, videoarea):
        OSD.setSize(self, videoarea, "MoreInfo")        
        marginOSD = math.floor(self.h/100)
        self.vbox.setContentsMargins(marginOSD, marginOSD, marginOSD, marginOSD)
        
    def showContent(self):
        self.lInfo.setText("<font style='color: white; font-size: " + self.fontsize + "px'>" + self.textInfo + "</font>")
        OSD.showContent(self)

class OSDNotify(OSD):
    def __init__(self, videoarea, parent):
        OSD.__init__(self, parent)
        
        ### Layout        
        self.lInfo = QtGui.QLabel(self)
        self.lInfo.setAlignment(QtCore.Qt.AlignCenter)      
        
        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.lInfo, 1)
        self.vbox.setSpacing(0)
        
        ### Variables
        self.text = "Rama"
        
        ### set Timer for OSD Display
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(3000)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.doHide)
        
        ### Class Settings
        self.setFontDivider(1.5)        
        
        ### Class postInit
        OSD.postInit(self, videoarea)
        
    def displayMessage(self, message):
        self.text = message
        self.showContent()
        self.doShow()
        
    def doHide(self):
        OSD.doHide(self)
        self.timer.stop()
    
    def doShow(self):
        OSD.doShow(self)
        self.timer.start()
        
    def setSize(self, videoarea):
        OSD.setSize(self, videoarea, "Notify")        
        marginOSD = math.floor(self.h/100)
        self.vbox.setContentsMargins(marginOSD, marginOSD, marginOSD, marginOSD)
        
    def showContent(self):
        self.lInfo.setText("<font style='color: white; font-size: " + self.fontsize + "px'>" + self.text + "</font>")
        OSD.showContent(self)
        
class OSDShutDown(OSDList):
    def __init__(self, videoarea, parent):
        OSDList.__init__(self, videoarea, parent)
        
        ### Variables
        self.listOfContent = [None]
        
        ### Layout
        self.lTitle = QtGui.QLabel(self)
        self.lHelp = QtGui.QLabel(self)
        self.lOption1 = QtGui.QLabel(self)
        self.lOption2 = QtGui.QLabel(self)
        self.lOption3 = QtGui.QLabel(self)
        
        self.listOfEntrys.append(self.lOption1)
        self.listOfEntrys.append(self.lOption2)
        self.listOfEntrys.append(self.lOption3)
        
        self.listOfContent.append(self.lOption1)
        self.listOfContent.append(self.lOption2)
        self.listOfContent.append(self.lOption3)
        
        hBox = QtGui.QHBoxLayout()
        hBox.setContentsMargins(0, 0, 0, 0)
        hBox.setSpacing(0)
        hBox.addWidget(self.lTitle, 1)
        hBox.addWidget(self.lHelp, 0)
        
        channelVBox = QtGui.QVBoxLayout(self)
        channelVBox.addLayout(hBox, 0)
        channelVBox.addWidget(self.lOption1, 1)
        channelVBox.addWidget(self.lOption2, 1)
        channelVBox.addWidget(self.lOption3, 1)
        channelVBox.setContentsMargins(0, 0, 0, 0)
        channelVBox.setSpacing(0)
        
        ### Class Settings
        self.typeOfList = "ShutDown"
        self.nrOfEntrys = 3
        self.setFontDivider(10)
        
        ### Class postInit
        OSDList.postInit(self, videoarea)
        
    def activateEntry(self):
        print(Kartina.interface.logout())
        if self.currentEntry == 0:
            self.parent.close()
        elif self.currentEntry == 1:
            os.system("sudo shutdown -h now")
        elif self.currentEntry == 2:
            os.system("sudo pm-suspend")
        
        
    def showContent(self):
        self.lTitle.setStyleSheet("background-color: #419934;")
        self.lTitle.setText("<font style='color: #000000; font-size: " + self.fontsize + "px'>&nbsp;<b>Wie ausschalten?</b></font>")
        helpfont = str(math.floor((int(self.fontsize)*7)/10))
        self.lHelp.setText("<font style='color: #FFFFFF; font-size: " + helpfont + "px'>&nbsp;<font style='color: #FF0000;'><b>⚪</b></font> Abbrechen&nbsp;</font>")
        self.lOption1.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;<b>✖ Rama Ausschalten</b></font>")
        self.lOption2.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;<b>◓ Herunterfahren</b></font>")
        self.lOption3.setText("<font style='color: #FFFFFF; font-size: " + self.fontsize + "px'>&nbsp;<b>◕ Bereitschaft</b></font>")
        OSDList.showContent(self, self.listOfContent)
        
    def applyContent(self, i, start, item):
        if self.currentEntry == i + start:
            self.highlightEntry(i)
