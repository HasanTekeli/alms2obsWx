import glob
import os
import wx
import wx.lib.mixins.listctrl as listmix
from funcs import create_data, organize_results


class resizedListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        tID = wx.ID_ANY
        dayTxt = wx.StaticText(self, -1, label="GÜNDÜZ", style=wx.ALIGN_CENTER)
        nightTxt = wx.StaticText(self, -1, label="AKŞAM", style=wx.ALIGN_CENTER)
        self.list_ctrl = resizedListCtrl(self, tID,
                                         style=wx.LC_REPORT
                                         | wx.BORDER_SUNKEN
                                         )
        self.list_ctrl.InsertColumn(0, 'Dosya Adı')
        self.list_ctrl.InsertColumn(1, 'Durum')
        self.list_ctrl.SetColumnWidth(0, 400)

        self.list_ctrlNight = resizedListCtrl(self, tID,
                                              style=wx.LC_REPORT
                                              | wx.BORDER_SUNKEN
                                              )
        self.list_ctrlNight.InsertColumn(0, 'Dosya Adı')
        self.list_ctrlNight.InsertColumn(1, 'Durum')
        self.list_ctrlNight.SetColumnWidth(0, 400)

        btn = wx.Button(self, label="Klasör seç")
        btn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(dayTxt, 0, wx.EXPAND, 5)
        sizer.Add(self.list_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(nightTxt, 0, wx.EXPAND, 5)
        sizer.Add(self.list_ctrlNight, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)

        self.folder_path = ""
        self.list_of_deps = {}

    def onOpenDirectory(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_path = dlg.GetPath()
            self.updateDisplay(organize_results(self.folder_path, self.list_of_deps))
        dlg.Destroy()

    def updateDisplay(self, mods_path):
        dayPath = glob.glob(mods_path + "day/*.*")
        nightPath = glob.glob(mods_path + "night/*.*")
        for index, path in enumerate(dayPath):
            self.list_ctrl.InsertItem(index, os.path.basename(path))
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onClickListItem, self.list_ctrl)
        for index, path in enumerate(nightPath):
            self.list_ctrlNight.InsertItem(index, os.path.basename(path))
        self.list_ctrlNight.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onClickListItem, self.list_ctrlNight)

    def onClickListItem(self, event):
        dayPath = self.folder_path + "/mods/day/"
        nightPath = self.folder_path + "/mods/night/"

        if "(İÖ)" in event.GetText():
            idx = event.GetIndex()
            item = self.list_ctrlNight.GetItem(idx)
            item_name = os.path.splitext(item.GetText())[0]
            self.list_ctrlNight.SetItem(idx, column=1, label="Kopyalandı")
            create_data(nightPath, item_name)
        else:
            idx = event.GetIndex()
            item = self.list_ctrl.GetItem(idx)
            item_name = os.path.splitext(item.GetText())[0]
            self.list_ctrl.SetItem(idx, column=1, label="Kopyalandı")
            create_data(dayPath, item_name)

    def updateStatus(self, folder_path):
        paths = glob.glob(folder_path + "/*.*")
        for index, path in enumerate(paths):
            self.list_ctrl.InsertItem(index, os.path.basename(path))


class MyFrame(wx.Frame):
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="alms2obsWx", size=(600, 600))
        panel = MyPanel(self)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()