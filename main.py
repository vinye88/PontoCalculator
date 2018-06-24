import wx
from LEDPanel import LEDPanel

app = wx.App()
LEDPanel(None, title='Ponto Calculator').Show()
app.MainLoop()