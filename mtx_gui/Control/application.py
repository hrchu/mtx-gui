# coding: utf-8

# Copyright (C) 2015 by Markus Rosjat<markus.rosjat@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
from mtx_gui.View import create_tk_root, start_tk_gui
from mtx_gui.View.MainWindow import MainWindow
from mtx_gui.View.widgets.frame import MCFrame, DataFrame, StorageFrame
from mtx_gui.View.widgets.menu import StorageSlotMenu, DataSlotMenu
from mtx_gui.Control.api import *
from mtx_gui.Control.observable import Observable

modul_logger = logging.getLogger('mtx-gui.control.application')


class Application(Observable):
    """ the controller class for the application
    """
    def __init__(self):
        super().__init__()
        self._mc = [mc for mc in get_devices() if mc.model.is_medium_changer()]
        self.view = MainWindow(create_tk_root())
        self.model = self
        self._ds = {}
        self._ss = {}
        self._widgets = []

    @property
    def mediumchangers(self):
        return self._mc

    def run(self):
        self.create_widgets()
        start_tk_gui(self.view)

    def create_widgets(self):
        """creating all the widgets in the main window"""
        self._widgets.append(MCFrame(self.view, self))

    def event_sink(self, callback_dict):
        sender = callback_dict['sender']
        event = callback_dict['event']
        action = callback_dict['action']
        if type(sender) == MediumChangerObserver and action == 'init':
            self._init_medium_changer_button(sender)
        if type(sender) == StorageSlotObserver and action == 'contextmenu':
            self._init_storage_slot_contextmenu(sender, event)
        if type(sender) == DataSlotObserver and action == 'contextmenu':
            self._init_data_slot_contextmenu(sender, event)

    def _init_medium_changer_button(self, sender):
        sender.model.get_data_slots()
        sender.model.get_storage_slots()
        self._ds.update({sender: get_data_slots(sender)})
        self._ss.update({sender: get_storage_slots(sender)})
        StorageFrame(self.view, self._ss[sender])
        DataFrame(self.view, self._ds[sender])
        for s in self._ss[sender]:
            s.application_callback = self.event_sink
        for s in self._ds[sender]:
            s.application_callback = self.event_sink

    def _init_storage_slot_contextmenu(self, sender, event):
        # figure what and where
        mc = [k for k, v in self._ss.items() if sender in v][0]
        with StorageSlotMenu(sender.view, mc.model.data_slots, tearoff=0) as popup:
            if sender.view.text != 'empty':
                modul_logger.debug('show contextmenu')
                popup.tk_popup(event.x_root, event.y_root, 0)

    def _init_data_slot_contextmenu(self, sender, event):
        # figure what and where
        mc = [k for k, v in self._ds.items() if sender in v][0]
        with DataSlotMenu(sender.view, mc.model.storage_slots, tearoff=0) as popup:
            if sender.view.text != 'empty':
                modul_logger.debug('show contextmenu')
                popup.tk_popup(event.x_root, event.y_root, 0)
