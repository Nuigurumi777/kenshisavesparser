import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin

import kenshisaves as ks

ignore_characters = set([])
additional_character_attrs = {}

class StatsPanel(wx.Panel, ColumnSorterMixin):
	def __init__(self, parent, num_cat):
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		
		self.my_category = ks.categories[num_cat]
		cols = ["Name"] + self.my_category["attributes"] + ["Comment"]
		self.ctrl_attributes_spreadsheet = wx.ListCtrl(self, style = wx.LC_REPORT)
		
		for i, s in enumerate(cols):
			self.ctrl_attributes_spreadsheet.InsertColumn(i + 1, s)
		
		self.n_columns = len(cols)
		ColumnSorterMixin.__init__(self, self.n_columns)
		
		self.itemDataMap = {}
		self.column_min_width = []
		for i in range(self.ctrl_attributes_spreadsheet.GetColumnCount()):
			self.ctrl_attributes_spreadsheet.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
			self.column_min_width.append(self.ctrl_attributes_spreadsheet.GetColumnWidth(i))
		
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.main_sizer.Add(self.ctrl_attributes_spreadsheet, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 10)
		self.SetSizer(self.main_sizer)
	
	def GetListCtrl(self):
		return self.ctrl_attributes_spreadsheet
	
	def Update(self):
		global additional_character_attrs
		con = self.ctrl_attributes_spreadsheet
		con.DeleteAllItems()
		self.itemDataMap = {}
		
		n_item = 0
		for character, attributes in ks.attribs.items():
			if character in ignore_characters: continue
			n_item = con.InsertItem(n_item, character)
			
			self.itemDataMap[n_item] = [character]
			for n_column, attr in enumerate(self.my_category["attributes"]):
				val = attributes[attr]
				con.SetItem(n_item, n_column+1, "%.02f\t" % val)
				self.itemDataMap[n_item].append(val)
			
			if character in additional_character_attrs.keys():
				if "color" in additional_character_attrs[character].keys():
					con.SetItemBackgroundColour(n_item, wx.Colour(additional_character_attrs[character]["color"]))
				if "comment" in additional_character_attrs[character].keys():
					con.SetItem(n_item, len(self.my_category["attributes"])+1, additional_character_attrs[character]["comment"])
					self.itemDataMap[n_item].append(additional_character_attrs[character]["comment"])
				
			con.SetItemData(n_item, n_item)
			n_item += 1
		con.SetColumnWidth(0, wx.LIST_AUTOSIZE)

class MainWindow(wx.Frame):
	
	def __init__(self, parent, id, title):
		global ignore_characters
		
		wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
		
		self.ReadSettings()
		self.ctrl_url = wx.TextCtrl(self, value = self.wildcard)
		self.bt_scan = wx.Button(self, label = "Update")
		self.bt_scan.Bind(wx.EVT_BUTTON, self.OnUpdate)
		
		self.nb = wx.Notebook(self)
		
		self.tabs = []
		for i, cat in enumerate(ks.categories):
			self.tabs.append(StatsPanel(self.nb, i))
			self.nb.AddPage(self.tabs[-1], cat["name"])		
		
		self.url_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.url_sizer.Add(self.ctrl_url, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 10)
		self.url_sizer.Add(self.bt_scan, flags = wx.SizerFlags().Right().Border(wx.ALL, 10))
		
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.main_sizer.Add(self.url_sizer, flags = wx.SizerFlags().Expand())
		self.main_sizer.Add(self.nb, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 10)
		
		self.SetSizer(self.main_sizer)
	
	def ReadSettings(self):
		global ignore_characters, additional_character_attrs
		with open("settings.txt") as f:
			for line in f:
				if line.startswith("#"): continue
				if line.startswith("wildcard"):
					self.wildcard = line.split("=")[1].strip()
				elif line.startswith("ignore"):
					ignore_characters = [x.strip() for x in line.split("=")[1].split(";")]
				elif line.startswith("@"):
					s = line[1:]
					char_names, char_attrs = [x.strip() for x in s.split("=")]
					char_names = [x.strip() for x in char_names.split(";")]
					char_attrs = [x.strip() for x in char_attrs.split(";")]
					for char_name in char_names:
						additional_character_attrs[char_name] = {}
						for ca in char_attrs:
							k, v = ca.split(":")
							additional_character_attrs[char_name][k.strip()] = v.strip()
						
	
	def OnUpdate(self, evt):
		global ignore_characters
		self.ReadSettings()
		ks.parse(self.ctrl_url.GetValue())
		
		#counting total and displayed characters
		#(can't check with set inclusion operation, because names may repeat)
		n_chars_total = 0
		n_chars_ignored = 0
		chars = list(ks.attribs.keys())
		for c in chars:
			n_chars_total += 1
			if c in ignore_characters: n_chars_ignored += 1
		self.SetTitle(f"Total {n_chars_total} characters, {n_chars_total - n_chars_ignored} displayed, {n_chars_ignored} ignored")
		for tab in self.tabs:
			tab.Update()

app = wx.App()
frame = MainWindow(None, -1, "Kenshi Saves Parser")
frame.Show(1)
app.MainLoop()