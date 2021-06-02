import glob
import os
import wx
import wx.lib.mixins.listctrl as listmix
import json
from funcs import create_data, organize_results


class ResizedListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
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
        self.list_ctrl = ResizedListCtrl(self, tID,
                                         style=wx.LC_REPORT
                                         | wx.BORDER_SUNKEN
                                         )
        self.list_ctrl.InsertColumn(0, 'Dosya Adı')
        self.list_ctrl.InsertColumn(1, 'Durum')
        self.list_ctrl.SetColumnWidth(0, 400)

        self.list_ctrlNight = ResizedListCtrl(self, tID,
                                              style=wx.LC_REPORT
                                              | wx.BORDER_SUNKEN
                                              )
        self.list_ctrlNight.InsertColumn(0, 'Dosya Adı')
        self.list_ctrlNight.InsertColumn(1, 'Durum')
        self.list_ctrlNight.SetColumnWidth(0, 400)

        btn = wx.Button(self, label="Klasör seç")
        btn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)

        pref_btn = wx.Button(self, wx.ID_ANY, label="Tercihler")
        pref_btn.Bind(wx.EVT_BUTTON, self.openPrefs)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(dayTxt, 0, wx.EXPAND, 5)
        sizer.Add(self.list_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(nightTxt, 0, wx.EXPAND, 5)
        sizer.Add(self.list_ctrlNight, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(pref_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(sizer)

        self.folder_path = ""
        self.list_of_deps = {}

    def openPrefs(self, event):
        dlg = PreferencesDialog()
        dlg.ShowModal()

    def onOpenDirectory(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_path = dlg.GetPath()
            self.updateDisplay(organize_results(self.folder_path, self.list_of_deps, current_dir))
        dlg.Destroy()

    def updateDisplay(self, mods_path):
        try:
            dayPath = glob.glob(mods_path + "day/*.*")
            nightPath = glob.glob(mods_path + "night/*.*")
            for index, path in enumerate(dayPath):
                self.list_ctrl.InsertItem(index, os.path.basename(path))
            self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onClickListItem, self.list_ctrl)
            for index, path in enumerate(nightPath):
                self.list_ctrlNight.InsertItem(index, os.path.basename(path))
            self.list_ctrlNight.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onClickListItem, self.list_ctrlNight)
        except TypeError:
            error_dlg = wx.MessageDialog(self, "Dosyalarınızdan birinde öğrenci numarası metin şeklinde yazılmış!\nLütfen düzeltip tekrar deneyin.", caption="Hata!")
            error_dlg.ShowModal()
            error_dlg.Destroy()
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


class PreferencesDialog(wx.Dialog):
    """
    Creates and displays a preferences dialog that allows the user to
    change some settings.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """
        Initialize the dialog
        """
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Preferences', size=(550, 300))
        self.cfg_file = current_dir + "/settings.json"
        with open(self.cfg_file, "r") as config:
            self.data = json.load(config)
        self.createWidgets()

    # ----------------------------------------------------------------------
    def createWidgets(self):
        """
        Create and layout the widgets in the dialog
        """
        lblSizer = wx.BoxSizer(wx.VERTICAL)
        valueSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.StdDialogButtonSizer()
        colSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.widgetNames = self.data
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)

        num_lbl = wx.StaticText(self, label="Numaraların olduğu hücre sütunu:")
        num_lbl.SetFont(font)
        grade_lbl = wx.StaticText(self, label="Notların olduğu hücre sütunu:")
        grade_lbl.SetFont(font)
        dep_lbl = wx.StaticText(self, label="Bölümün/Dersin yazdığı bir hücre (Örn. C2):")
        dep_lbl.SetFont(font)
        lblSizer.Add(num_lbl, 0, wx.ALL, 10)
        lblSizer.Add(grade_lbl, 0, wx.ALL, 10)
        lblSizer.Add(dep_lbl, 0, wx.ALL, 10)
        num_value = self.data["num_col"]
        grade_value = self.data["grade_col"]
        dep_value = self.data["dep_cell"]
        num_txt = wx.TextCtrl(self, value=num_value, name="num_col")
        grade_txt = wx.TextCtrl(self, value=grade_value, name="grade_col")
        dep_txt = wx.TextCtrl(self, value=dep_value, name="dep_cell")
        valueSizer.Add(num_txt, 0, wx.ALL | wx.EXPAND, 5)
        valueSizer.Add(grade_txt, 0, wx.ALL | wx.EXPAND, 5)
        valueSizer.Add(dep_txt, 0, wx.ALL | wx.EXPAND, 5)

        saveBtn = wx.Button(self, wx.ID_OK, label="Save")
        saveBtn.Bind(wx.EVT_BUTTON, self.onSave)
        btnSizer.AddButton(saveBtn)

        cancelBtn = wx.Button(self, wx.ID_CANCEL)
        btnSizer.AddButton(cancelBtn)

        depButton = wx.Button(self, wx.ID_OPEN, label="Departments")
        depButton.Bind(wx.EVT_BUTTON, self.openDepList)
        lblSizer.AddSpacer(10)
        lblSizer.Add(depButton)
        btnSizer.Realize()

        colSizer.Add(lblSizer)
        colSizer.Add(valueSizer, 1, wx.EXPAND)
        mainSizer.Add(colSizer, 0, wx.EXPAND)
        mainSizer.Add(btnSizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.SetSizer(mainSizer)

    # ----------------------------------------------------------------------
    def onSave(self, event):
        """
        Saves values to disk
        """
        for name in self.widgetNames:
            widget = wx.FindWindowByName(name)
            if isinstance(widget, wx.TextCtrl):
                value = widget.GetValue()
                self.widgetNames[name] = value
            else:
                pass

        with open(self.cfg_file, "w") as config:
            json.dump(self.data, config, ensure_ascii=False, indent=4)
        self.EndModal(0)

    def openDepList(self, event):
        dlg = DepartmentsDialog()
        dlg.ShowModal()


class DepartmentsDialog(wx.Dialog):
    """
    Creates and displays a dialog where departments are listed.
    """
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Departments', size=(400, 700))

        self.cfg_file = "settings.json"
        with open(self.cfg_file, "r") as config:
            self.data = json.load(config)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        txt = 'Bölüm Arayın. Büyük-küçük "İ-i" harfine dikkat edin.'
        label = wx.StaticText(self, label=txt)

        self.main_sizer.Add(label, 0, wx.ALL, 5)
        self.search = wx.SearchCtrl(
            self, style=wx.TE_PROCESS_ENTER, size=(-1, 25))
        self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.on_search)

        self.main_sizer.Add(self.search, 0, wx.EXPAND)

        self.choices = self.data["departments"]

        self.dep_list_lbo = wx.ListBox(self,
                                      size=wx.DefaultSize, choices=self.choices,
                                      style=wx.LB_NEEDED_SB | wx.CB_READONLY,
                                      )
        self.dep_list_lbo.Set(self.choices)
        self.search_results_lbo = wx.ListBox(self,
                                      size=(10,-1),
                                      style=wx.LB_NEEDED_SB | wx.CB_READONLY,
                                      )

        txt_src_res = "Search Results"
        lbl_src_res = wx.StaticText(self, label=txt_src_res)
        self.main_sizer.Add(lbl_src_res, 0, wx.EXPAND)
        self.main_sizer.Add(self.search_results_lbo, 2, wx.EXPAND)
        txt_all_deps = "All Departments"
        lbl_all_deps = wx.StaticText(self, label=txt_all_deps)
        add_dep_btn = wx.Button(self, wx.ID_ANY, label="Yeni Bölüm / Ders Ekleyin")
        add_dep_btn.Bind(wx.EVT_BUTTON, self.add_dep)

        refresh_txt = "Yeni eklediğiniz bölümlerin görünmesi için listeyi yenileyin:"
        refresh_lbl = wx.StaticText(self, label=refresh_txt)
        refresh_btn = wx.Button(self, wx.ID_ANY, label="Listeyi yenile")
        refresh_btn.Bind(wx.EVT_BUTTON, self.refresh_deps)
        self.main_sizer.Add(lbl_all_deps, 0, wx.EXPAND)
        self.main_sizer.Add(self.dep_list_lbo, 3, wx.EXPAND)
        self.main_sizer.Add(add_dep_btn, 1, wx.ALL | wx.ALIGN_CENTER)
        self.main_sizer.Add(refresh_lbl, 0, wx.ALL | wx.ALIGN_CENTER)
        self.main_sizer.Add(refresh_btn, 0, wx.ALL | wx.ALIGN_CENTER)


        self.main_sizer.AddSpacer(30)

        self.SetSizer(self.main_sizer)

    def refresh_deps(self, event):
        with open(self.cfg_file, "r") as config:
            self.data = json.load(config)
            choices = self.data["departments"]
            self.dep_list_lbo.Set(choices)

    def on_search(self, event):
        search_term = self.search.GetValue()
        filtered = [x for x in self.choices if search_term.lower() in x.lower()]

        self.update_search_results(filtered)
        return filtered

    def update_search_results(self, filtered):
        self.search_results_lbo.Clear()
        self.search_results_lbo.Append(filtered)

    def add_dep(self, event):
        add_dep_dlg = AddDepDlg()
        add_dep_dlg.ShowModal()


class AddDepDlg(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Bölüm / Ders Ekle', size=(200, 200))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.cfg_file = "settings.json"
        txt = 'Bölüm / ders ekleyin:'
        label = wx.StaticText(self, label=txt)
        self.main_sizer.Add(label, 1, wx.EXPAND, 5)
        self.dep_txt = wx.TextCtrl(self, name="new_dep_name")
        self.dep_btn = wx.Button(self, wx.ID_ANY, label="Kaydet")
        self.dep_btn.Bind(wx.EVT_BUTTON, self.add_new)
        self.main_sizer.Add(self.dep_txt, 1, wx.EXPAND, 3)
        self.main_sizer.AddSpacer(30)
        self.main_sizer.Add(self.dep_btn, 1, wx.ALL | wx.ALIGN_CENTER)
        with open(self.cfg_file, "r") as config:
            self.data = json.load(config)
            self.num_col = self.data["num_col"]
            self.grade_col = self.data["grade_col"]
            self.departments = self.data["departments"]
        self.SetSizer(self.main_sizer)

    def add_new(self, event):
        value = self.dep_txt.GetValue()

        with open(self.cfg_file, "w") as configw:
            self.departments.append(value)
            all_data = {"num_col": self.num_col, "grade_col": self.grade_col, "departments": self.departments}

            json.dump(all_data, configw, indent=4, ensure_ascii=False)

        wx.Window.Close(self)


if __name__ == "__main__":
    app = wx.App(False)
    current_dir = os.getcwd()
    frame = MyFrame()
    app.MainLoop()