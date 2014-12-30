# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import sys, time, math, vlc, Kartina, OSD

class VideoPlayer(QtGui.QFrame):
    def __init__(self, parent = None):
        super(VideoPlayer, self).__init__(parent)
        
        self.Instance = vlc.Instance()
        self.MediaPlayer = self.Instance.media_player_new()
        self.MediaPlayer.video_set_scale(0)
        
        self.currentChannelID = Kartina.interface.channelList.getGroups()[0].getChannels()[1].getID()
        
        self.setGeometry(0, 0, 1024, 576)
               
        Palette = self.palette()
        Palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0,0,0))
        self.setPalette(Palette)
        self.setAutoFillBackground(True)
        
        self.playingArchive = False
        self.playPosition = Kartina.getTime()
        self.titlePosition = 0
        
        self.connect(OSD.delayTimer, QtCore.SIGNAL("timeout()"), self.addToDelayTimeBuffer)
        
        self.playTimeBuffer = 0
        self.playTime = QtCore.QTimer(self)
        self.playTime.setInterval(1000)
        self.connect(self.playTime, QtCore.SIGNAL("timeout()"), self.addToPlayTimeBuffer)

        self.OSDRefreshTimer = QtCore.QTimer(self)
        self.OSDRefreshTimer.setInterval(50)
        self.connect(self.OSDRefreshTimer, QtCore.SIGNAL("timeout()"), self.refreshOSD)
        self.OSDRefreshTimer.start()
        
        self.Clist = OSD.OSDChannelList(self.getGeometry(), parent)
        self.EPG = OSD.OSDEPG(self.getGeometry(), parent)
        self.Info = OSD.OSDInfo(self.getGeometry(), parent)
        self.MoreInfo = OSD.OSDMoreInfo(self.getGeometry(), parent)
        self.Notify = OSD.OSDNotify(self.getGeometry(), parent)
        self.ShutDown = OSD.OSDShutDown(self.getGeometry(), parent)
        
        self.loadStream(self.playPosition, True)
        
    def addToDelayTimeBuffer(self):
        if not self.Video.playingArchive:
            OSD.pausedelay = OSD.pausedelay + 1
        
    def toggleCrop(self):
        geo = self.getGeometry()
        w = geo.width()
        if self.MediaPlayer.video_get_scale() == 0:
            self.Notify.displayMessage("LetterBox On")
            self.MediaPlayer.video_set_scale(w/self.MediaPlayer.video_get_size()[0])
        else:
            self.Notify.displayMessage("LetterBox Off")
            self.MediaPlayer.video_set_scale(0)
        
    def toggleAspectRatio(self):
        if self.MediaPlayer.video_get_aspect_ratio() == None:
            aspect_ratio = str.encode("16:9", "utf-8")
        elif self.MediaPlayer.video_get_aspect_ratio() == str.encode("16:9", "utf-8"):
            aspect_ratio = str.encode("4:3", "utf-8")
        elif self.MediaPlayer.video_get_aspect_ratio() == str.encode("4:3", "utf-8"):
            aspect_ratio = None
        self.MediaPlayer.video_set_aspect_ratio(aspect_ratio)

    def refreshOSD(self):
        self.Clist.update()
        self.EPG.update()
        self.Info.update()
        self.MoreInfo.update()
        self.Notify.update()
        self.ShutDown.update()
        
    def addToPlayTimeBuffer(self):
        if self.MediaPlayer.is_playing() == 1:
            self.playTimeBuffer = self.playTimeBuffer + 1
        if self.playingArchive:
            self.Info.showContent()
        
    def jump(self, jump):
        playTime = self.playTimeBuffer        
        if int(self.playPosition) + playTime + jump <= Kartina.getTime() + Kartina.timeshift - 15*60:
            self.playPosition = int(self.playPosition) + playTime + jump
            OSD.pausedelay = OSD.pausedelay - jump
            self.loadStream(self.playPosition, True)
            if jump > 0:
                notifytext = "▶▶ " + str(int(jump/60)) + " Min"
            else:
                notifytext = "◀◀ " + str(int(abs(jump)/60)) + " Min"
        else:
            notifytext = "☹"
        self.Notify.displayMessage(notifytext)
        
    def setMode(self, mode):
        OSD.archivePlayBuffer = 0
        OSD.pausedelay = 0
        if mode == "normal":
            self.playingArchive = False
            self.Info.doShow()
        if mode == "archive":
            self.playingArchive = True
            self.Info.doShow()
        
    def setSize(self, x, y, w, h):
        self.setGeometry(x, y, w, h)
        self.EPG.setSize(self.getGeometry())
        self.Clist.setSize(self.getGeometry())
        self.Info.setSize(self.getGeometry())
        self.MoreInfo.setSize(self.getGeometry())
        self.Notify.setSize(self.getGeometry())
        self.ShutDown.setSize(self.getGeometry())
        self.EPG.showContent()
        self.Clist.showContent()
        self.Info.showContent()
        self.MoreInfo.showContent()
        self.Notify.showContent()
        self.ShutDown.showContent()
        
    def getGeometry(self):
        return self.frameGeometry()
        
    def loadStream(self, position, play = False):
        self.playPosition = position
        stream = Kartina.interface.getURL(self.currentChannelID, position)
        stream = stream.replace('http/ts', 'http')
        self.Media = self.Instance.media_new_location(stream.encode('utf-8'))
        self.Media.add_options(str.encode("http-caching=1500", "utf-8"), str.encode("no-http-reconnect", "utf-8"), str.encode("filter=crop", "utf-8"))
        self.MediaPlayer.set_media(self.Media)
        if sys.platform == "linux2":
            self.MediaPlayer.set_xwindow(self.winId())
        elif sys.platform == "win32":
            self.MediaPlayer.set_hwnd(self.winId())
        elif sys.platform == "darwin":
            self.MediaPlayer.set_agl(self.windId())
        if play == True:
            self.MediaPlayer.play()
        self.playTimeBuffer = 0
        self.playTime.start()
        self.MediaPlayer.video_set_scale(0)
