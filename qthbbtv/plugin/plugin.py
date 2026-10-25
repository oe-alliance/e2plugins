from __future__ import absolute_import, print_function

from enigma import iPlayableService, iServiceInformation

from Components.ServiceEventTracker import ServiceEventTracker
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar
from Screens.Screen import Screen

from .hbbtv import HbbTVWindow


class HBBTVParser(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.started = False
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
		self.openUrl = False

	def serviceStarted(self):
		if self.started:
			return
		if InfoBar.instance:
			InfoBar.instance.onHBBTVActivation.append(self.onHBBTVActivation)
			self.started = True

	def onHBBTVActivation(self):
		self.openUrl = False
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		# An earlier red-button callback may already have stopped the service.
		if info is None:
			print("[QtHbbtv] Ignoring activation: no current service information.")
			return
		startUrl = info.getInfoString(iServiceInformation.sHBBTVUrl)
		if not startUrl:
			print("[QtHbbtv] Ignoring activation: no HbbTV application URL.")
			return
		width = info and info.getInfo(iServiceInformation.sVideoWidth) or -1
		height = info and info.getInfo(iServiceInformation.sVideoHeight) or -1
		pmt = info and info.getInfo(iServiceInformation.sPMTPID) or -1
		tsid = info and info.getInfo(iServiceInformation.sTSID) or -1
		onid = info and info.getInfo(iServiceInformation.sONID) or -1
		ssid = info and info.getInfo(iServiceInformation.sSID) or -1

		print('URL %s' % (startUrl))
		print('PMT %d TSID %d ONID %d SSID %d' % (pmt, tsid, onid, ssid))

		ait = info.getAITApplications()

		self.openUrl = startUrl
		self.session.open(HbbTVWindow, self.openUrl, pmt, tsid, onid, ssid, width, height, ait)


def autostart(reason, **kwargs):
	if 'session' in kwargs:
		HBBTVParser(kwargs['session'])


def Plugins(**kwargs):
	return PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart)
