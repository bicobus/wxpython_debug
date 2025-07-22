#!/usr/bin/env python
# -*- coding: utf-8 -*-
# © 2024 bicobus <bicobus@keemail.me>

import wx
from wx.lib import expando

DEFAULT_IMAGE = None
TEST_DATA = {
    "l_1": {
        "text": "test 1",
        "img": "imgs/test_0.png",
        "options": [
            {"label": "goto 1 1", "target": "l_1_1"},
            {"label": "goto 2", "target": "l_2"},
            {"label": "END 1"}
        ],
    },
    "l_1_1": {
        "text": "test 1 1",
        "img": "imgs/test_1.png",
        "options": [{"label": "END 1 1"}],
    },
    "l_2": {
        "text": "test 2",
        "img": "imgs/test_2.png",
        "options": [{"label": "END 2"}]
    }
}


class RunApp(wx.App):
    def OnInit(self):
        frame = BaseWindow(None)
        frame.Show(True)
        return True


class BaseWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent, title="Base window", size=(700, 650), pos=wx.DefaultPosition
        )
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        button1 = wx.Button(panel, wx.ID_ANY, "Preview: legacy")
        button2 = wx.Button(panel, wx.ID_ANY, "Preview: destruction")
        version_info = wx.StaticText(panel, wx.ID_ANY, "Version: %s" % wx.version())
        sizer.Add(button1)
        sizer.Add(button2)
        sizer.Add(version_info)
        panel.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_click, button1)
        self.Bind(wx.EVT_BUTTON, self.on_click2, button2)

    def on_click(self, evt):
        self.previewframe = wx.Frame(
            self, size=(445, 805), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        )
        self.previewframe.Bind(wx.EVT_CLOSE, self.preview_on_close)
        self.previewframe.SetTitle("Preview: legacy")
        PreviewEvent(self.previewframe, TEST_DATA['l_1'])
        self.previewframe.Center()
        self.previewframe.Show()
        return

    def on_click2(self, evt, data=None):
        self.previewframe = wx.Frame(
            self, size=(445, 805), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        )
        self.previewframe.Bind(wx.EVT_CLOSE, self.preview_on_close)
        self.previewframe.SetTitle("Preview: destruction")
        data = TEST_DATA['l_1'] if not data else data
        PreviewEvent2(self.previewframe, data)
        self.previewframe.Center()
        self.previewframe.Show()

    def preview_on_close(self, evt):
        self.previewframe.Destroy()
        self.previewframe = None


class PreviewEvent(wx.Panel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_ERASE)
        self.frame = parent
        self.background_img = None

        self.set_bgimg(data)
        self.build_widgets(data)

        self.Layout()
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)

    def set_bgimg(self, data):
        try:
            self.background_img = data["img"]
        except KeyError:
            self.background_img = DEFAULT_IMAGE

    def build_widgets(self, data):
        vsizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        text = expando.ExpandoTextCtrl(
            self,
            wx.ID_ANY,
            value=data["text"],
            style=wx.TE_WORDWRAP | wx.TE_READONLY,
        )
        text.SetMaxHeight(400)
        vsizer.Add(text, 0, wx.EXPAND | wx.ALL, 5)
        vsizer.Add((1, 1), 1, wx.EXPAND)
        buttonxtra = {"style": wx.BORDER_STATIC, "size": (-1, 20)}
        for opt in data["options"]:
            if "target" not in opt or not opt["target"]:
                btn = wx.Button(self, label=opt["label"], **buttonxtra)
                btn.SetBackgroundColour("#FF6666")
                btn.Bind(wx.EVT_BUTTON, lambda evt: self.GetParent().Close(), btn)
                sizer.Add(btn, 0, wx.ALL, 5)
            else:
                btn = wx.Button(self, label=opt["label"], **buttonxtra)
                btn.data_key = opt["target"]
                self.Bind(wx.EVT_BUTTON, self.on_button_clicked, btn)
                sizer.Add(btn, 0, wx.ALL, 5)
        hsizer.Add((1, 1), 1, wx.EXPAND)
        hsizer.Add(sizer, 0, wx.TOP, 100)
        hsizer.Add((1, 1), 0, wx.ALL, 75)
        vsizer.Add(hsizer, 0, wx.ALL, 5)
        vsizer.Add((1, 1), 0, wx.ALL, 75)
        self.SetSizer(vsizer)

    def on_button_clicked(self, evt):
        wdg = evt.GetEventObject()
        if wdg.data_key not in TEST_DATA.keys():
            return False
        data = TEST_DATA[wdg.data_key]
        self.DestroyChildren()
        self.ClearBackground()
        self.set_bgimg(data)
        self.build_widgets(data)
        self.Layout()
        self.Refresh()

    def get_bitmap(self, img):
        if isinstance(img, wx.Bitmap):
            return img
        return wx.Bitmap(str(img), wx.BITMAP_TYPE_PNG)

    def on_erase_background(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRegion(rect)
        dc.Clear()
        dc.DrawBitmap(self.get_bitmap(self.background_img), 0, 0)


class PreviewEvent2(PreviewEvent):
    def on_button_clicked(self, evt):
        wdg = evt.GetEventObject()
        if wdg.data_key not in TEST_DATA.keys():
            return False
        data = TEST_DATA[wdg.data_key]
        self.frame.GetParent().on_click2(evt=None, data=data)
        self.frame.Hide()
        self.Destroy()


if __name__ == '__main__':
    app = RunApp()
    app.MainLoop()
