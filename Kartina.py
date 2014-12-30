# -*- coding: utf-8 -*-
import urllib2

import xml.dom.minidom
import time, math

def dokument(domina):
    for node in domina.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
            print("<" + node.nodeName + ">")
        elif node.nodeType == node.TEXT_NODE:
            print(node.nodeValue.strip())
       # elif node.nodeType == node.COMMENT_NODE:
       #     print("Typ COMMENT_NODE, ")
        dokument(node)

kapi = "http://iptv.kartina.tv/api/xml/"
timeshift = 1 * 3600

def getTime():
    return math.floor(time.time() - timeshift)

class KartinaError(Exception):
    def __init__(self, dom):
        self.dom = dom
        print(self.dom.getElementsByTagName("message")[0].childNodes[0].data)

class API:
    def __init__(self, login, password):
        self.opener =  urllib2.build_opener()
        url = kapi + "login?login=" + login + "&pass=" + password        
        dom = self.getDOM(url)
        
        self.sid = dom.getElementsByTagName("sid")[0].childNodes[0].data
        self.sid_name = dom.getElementsByTagName("sid_name")[0].childNodes[0].data
        self.expire = dom.getElementsByTagName("packet_expire")[0].childNodes[0].data
        self.opener.addheaders.append(('Cookie', self.sid_name + "=" + self.sid))
        
        self.channelList = ChannelList(self)
        
    def getDOM(self, url):        
        dom = xml.dom.minidom.parse(self.opener.open(url))
        try:
            dom.getElementsByTagName("message")[0].childNodes[0].data
            raise KartinaError(dom)
        except IndexError:
            return dom
        
    def getChannelListDOM(self):
        url = kapi + "channel_list"
        dom = self.getDOM(url)
        return dom

    def getURL(self, cid, position):
        if Channel.getByID(self, cid).getArchive():      
            url = kapi + "get_url?cid=" + cid + "&gmt=" + str(int(position))
        else:
            url = kapi + "get_url?cid=" + cid
        try:
            dom = self.getDOM(url)
        except KartinaError:
            dom = self.getDOM(kapi + "get_url?cid=" + cid)
        return dom.getElementsByTagName("url")[0].childNodes[0].data
        
    def getEPGDOM(self, cid, day):
        url = kapi + "epg?cid=" + cid + "&day=" + day
        dom = self.getDOM(url)
        return dom
        
    def getEPGNextDOM(self, cid):
        url = kapi + "epg_next?cid=" + cid
        dom = self.getDOM(url)
        return dom
        
    def logout(self):
        url = kapi + "logout"
        dom = xml.dom.minidom.parse(self.opener.open(url))
        return dom.getElementsByTagName("message")[0].childNodes[0].data
        
class ChannelList:
    def __init__(self, api):
        self.api = api
        self.groups = []
        self.fillList()
    
    def getGroups(self):
        return self.groups
        
    def addGroup(self, group):
        self.groups.append(group)
        
    def fillList(self):
        dom = self.api.getChannelListDOM()
        for e in dom.firstChild.childNodes:
            if e.nodeName == "groups":
                for groups in e.childNodes:
                    if groups.nodeName == "item":
                        groupid = groups.childNodes[0].firstChild.data
                        groupname = groups.childNodes[1].firstChild.data
                        groupcolor = groups.childNodes[2].firstChild.data
                        self.addGroup(ChannelGroup(self.api, groupid, groupname, groupcolor, groups.childNodes, self))
    
class ChannelGroup:
    def __init__(self, api, id, name, color, dom, channellist):
        self.api = api
        self.id = id
        self.name = name
        self.color = color
        self.channels = [None]
        self.fillGroup(dom)
    
    def getID(self):
        return self.id
    
    def getName(self):
        return self.name
        
    def getColor(self):
        return self.color
    
    def getChannels(self):
        return self.channels
    
    def addChannel(self, channel):
        self.channels.append(channel)
        
    def fillGroup(self, dom):
        for e in dom:
            if e.nodeName == "channels":
                for channels in e.childNodes:
                    if channels.nodeName == "item":
                        cicon = None
                        carchive = 0
                        cepg_start = 0
                        for item in channels.childNodes:                            
                            if item.nodeName == "id":
                                cid = item.firstChild.data
                            if item.nodeName == "name":
                                cname = item.firstChild.data
                            if item.nodeName == "icon":
                                cicon = item.firstChild.data
                            if item.nodeName == "have_archive":
                                carchive = item.firstChild.data
                            if item.nodeName == "epg_start":
                                cepg_start = item.firstChild.data
                        if cname[-2] == "-":
                            cname = cname[:-3]
                        self.addChannel(Channel(self.api, cid, cname, cicon, self, carchive, cepg_start))
                        
class Channel:    
    @classmethod    
    def getByID(self, api, id):
        for group in api.channelList.getGroups():
            for channel in group.getChannels():
                if channel != None and channel.getID() == id:
                    return channel
        
    def __init__(self, api, id, name, icon, group, archive, epg_start):
        self.api = api
        self.id = id
        self.name = name
        self.group = group
        self.icon = icon
        self.archive = archive
        self.epg_start = epg_start
        self.epg = []
             
    def getID(self):
        return self.id
    
    def getName(self):
        return self.name
        
    def getIcon(self):
        return self.icon
        
    def getArchive(self):
        if self.archive == "1":
            return True
        else:
            return False
    
    def getGroup(self):
        return self.group
        
    def getEPGStart(self):
        return self.epg_strart
        
    def getEPG(self):
        return self.epg
    
    def getShow(self, cid):
        dom = self.api.getEPGNextDOM(cid)
        return dom.firstChild.childNodes[0].childNodes[0].childNodes[0].firstChild.data
        
    def addEPGItem(self, time, name):
        item = [time, name]
        self.epg.append(item)
        
    def fillEPG(self, day):
        if self.epg == [] or self.epg[0] != day:
            self.epg = []
            self.epg.append(day)
            dom = self.api.getEPGDOM(self.id, day)
            for e in dom.firstChild.childNodes:
                if e.nodeName == "epg":
                    for epg in e.childNodes:
                        self.addEPGItem(epg.childNodes[0].firstChild.data, epg.childNodes[1].firstChild.data)
                        
interface = API('140', '041')
