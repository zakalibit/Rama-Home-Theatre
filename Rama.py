#!/usr/bin/env python

import sys, Kartina, Video, OSD
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.resize(1024, 576)
        self.setWindowTitle('Rama')
        
        self.Video = Video.VideoPlayer(self)              
        
        self.desktop = QtGui.QApplication.desktop()  
        
        self.Video.setMode("normal")
        self.Video.Clist.showContent()
        
        QtGui.QShortcut(QtGui.QKeySequence("F"), self, self.toggleFullScreen)
        QtGui.QShortcut(QtGui.QKeySequence("I"), self, self.keyInfo)
        QtGui.QShortcut(QtGui.QKeySequence("X"), self, self.turnOff)
        
        QtGui.QShortcut(QtGui.QKeySequence("Up"), self, self.keyUp)
        QtGui.QShortcut(QtGui.QKeySequence("Down"), self, self.keyDown)
        QtGui.QShortcut(QtGui.QKeySequence("Left"), self, self.keyLeft)
        QtGui.QShortcut(QtGui.QKeySequence("Right"), self, self.keyRight)
        QtGui.QShortcut(QtGui.QKeySequence("Return"), self, self.keyReturn)
        QtGui.QShortcut(QtGui.QKeySequence("BackSpace"), self, self.keyBack)
        
        QtGui.QShortcut(QtGui.QKeySequence("P"), self, self.keyPlayPause)
        QtGui.QShortcut(QtGui.QKeySequence("S"), self, self.keyStop)
        
        QtGui.QShortcut(QtGui.QKeySequence("F5"), self, self.keyRed)
        QtGui.QShortcut(QtGui.QKeySequence("F6"), self, self.keyGreen)
        
        QtGui.QShortcut(QtGui.QKeySequence("F9"), self, self.keyAspectRatio)
        QtGui.QShortcut(QtGui.QKeySequence("F10"), self, self.keyCrop)
        
        QtGui.QShortcut(QtGui.QKeySequence("H"), self, self.keyRewind)
        QtGui.QShortcut(QtGui.QKeySequence("J"), self, self.keyForward)
        QtGui.QShortcut(QtGui.QKeySequence("K"), self, self.keyPrevious)
        QtGui.QShortcut(QtGui.QKeySequence("L"), self, self.keyNext)
            
    def keyCrop(self):
        self.Video.toggleCrop()
            
    def keyAspectRatio(self):
        self.Video.toggleAspectRatio()
        
    def keyPrevious(self):
        if self.Video.playingArchive:
            OSD.archivePlayBuffer = OSD.archivePlayBuffer + self.Video.playTimeBuffer
        self.Video.jump(-600)
        
    def keyNext(self):
        if self.Video.playingArchive:
            OSD.archivePlayBuffer = OSD.archivePlayBuffer + self.Video.playTimeBuffer
        self.Video.jump(600)
        
    def keyRewind(self):
        if self.Video.playingArchive:
            OSD.archivePlayBuffer = OSD.archivePlayBuffer + self.Video.playTimeBuffer
        self.Video.jump(-60)
        
    def keyForward(self):
        if self.Video.playingArchive:
            OSD.archivePlayBuffer = OSD.archivePlayBuffer + self.Video.playTimeBuffer
        self.Video.jump(60)
        
    def turnOff(self):
        self.Video.ShutDown.toggleVisible()
        
    def keyInfo(self):
            if not self.Video.Info.isVisible() and not self.Video.EPG.isVisible():
                self.Video.Info.toggleVisible()  
            elif self.Video.Info.isVisible() or self.Video.EPG.isVisible():
                self.Video.MoreInfo.toggleVisible()
        
    def keyUp(self):
            if self.Video.ShutDown.isVisible():
                self.Video.ShutDown.goUp()
            elif self.Video.EPG.isVisible():
                self.Video.EPG.goUp()
            elif self.Video.Clist.isVisible():
                self.Video.Clist.goUp()
        
    def keyDown(self):
            if self.Video.ShutDown.isVisible():
                self.Video.ShutDown.goDown()
            elif self.Video.EPG.isVisible():
                self.Video.EPG.goDown()
            elif self.Video.Clist.isVisible():
                self.Video.Clist.goDown()
                
    def keyLeft(self):
            if self.Video.EPG.isVisible():
                self.Video.EPG.prevList()
            elif self.Video.Clist.isVisible():
                self.Video.Clist.prevList()
                
    def keyRight(self):
            if self.Video.EPG.isVisible():
                self.Video.EPG.nextList()
            elif self.Video.Clist.isVisible():
                self.Video.Clist.nextList()
                
    def keyReturn(self):
            if self.Video.ShutDown.isVisible():
                self.Video.ShutDown.activateEntry()
            elif self.Video.EPG.isVisible():
                self.Video.EPG.activateEntry()
            elif self.Video.Clist.isVisible():
                self.Video.Clist.activateEntry()
            elif not self.Video.Clist.isVisible() and not self.Video.EPG.isVisible():
                self.Video.Info.toggleVisible()
                
    def keyRed(self):
        if self.Video.EPG.isVisible():
            self.Video.EPG.doHide()
        elif self.Video.Clist.isVisible():
            self.Video.Clist.startEPG()
        else:
            self.Video.Clist.doShow()

    def keyGreen(self):
        if self.Video.Info.isVisible():
            self.Video.EPG.doShow()
            
    def keyBack(self):
        if self.Video.EPG.isVisible():
            self.Video.EPG.doHide()
        elif self.Video.Clist.isVisible():
            self.Video.Clist.doHide()
        elif not self.Video.EPG.isVisible() and not self.Video.Clist.isVisible():
            self.Video.Info.doHide()
            self.Video.MoreInfo.doHide()
    
    def keyPlayPause(self):
        if self.Video.MediaPlayer.is_playing() == 1:
            self.Video.MediaPlayer.pause()
            OSD.delayTimer.start()
            self.Video.Notify.displayMessage("▮▮")
        else:
            self.Video.MediaPlayer.play()
            OSD.delayTimer.stop()
            self.Video.Notify.displayMessage("▶")
    
    def keyStop(self):
        if OSD.pausedelay != 0 or self.Video.playingArchive:
            OSD.pausedelay = 0
            self.Video.totalJump = 0
            OSD.delayTimer.stop()
            self.Video.loadStream(Kartina.getTime(), True)
            self.Video.Notify.displayMessage("◼")
            self.Video.setMode("normal")

    def toggleFullScreen(self):
        if not self.isFullScreen():   
            width = self.desktop.screenGeometry().width()
            height = self.desktop.screenGeometry().height()      
            self.Video.setSize(0, 0, width, height)
            self.showFullScreen()
        else:
            self.Video.setSize(0, 0, 1024, 576)
            self.showNormal()

app = QtGui.QApplication(sys.argv)
app.setApplicationName("Rama")
main = MainWindow()
main.show()
sys.exit(app.exec_())
