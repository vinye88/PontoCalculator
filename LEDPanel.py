import wx, json, re
from datetime import datetime, date
from enum import Enum
import wx.gizmos as gizmos

class LEDPanel(wx.Frame):
    class SaidaStates(Enum):
        MIN = 'Saída Mínima'
        NORMAL = 'Saída'
        MAX = 'Saída Máxima'

    def __init__(self, *args, **kwargs):
        super(LEDPanel, self).__init__(*args, **kwargs)
        self.InitUI()

    def adjust_menu(self):
        super(LEDPanel, self).SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        super(LEDPanel, self).SetSize((540,180))
        menubar = wx.MenuBar()

        config_menu = wx.Menu()
        config_setturno1_item = config_menu.Append(-1, '1º turno')
        config_setalmoco_item = config_menu.Append(-1, 'Almoço')
        config_setgordura_item = config_menu.Append(-1, 'Gordura')

        menubar.Append(config_menu, '&Configurar')

        ajuda_menu = wx.Menu()
        ajuda_sobre = ajuda_menu.Append(-1, 'Sobre')

        menubar.Append(ajuda_menu, '&Ajuda')

        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.setTurno1, config_setturno1_item)
        self.Bind(wx.EVT_MENU, self.setAlmoco, config_setalmoco_item)
        self.Bind(wx.EVT_MENU, self.setGordura, config_setgordura_item)
        self.Bind(wx.EVT_MENU, self.displayAjuda, ajuda_sobre)

    def adjust_jornada(self):
        jornadaL = wx.BoxSizer(wx.HORIZONTAL)
        x = 130
        sizeL = (x,17)
        style=wx.ALIGN_CENTRE
        
        self.txts = [
            wx.StaticText(self,-1, 'Entrada', size=sizeL, style=style),
            wx.StaticText(self,-1, 'Saida Almoço', size=sizeL, style=style),
            wx.StaticText(self,-1, 'Entrada 2', size=sizeL, style=style),
            wx.StaticText(self,-1, self.SaidaStates.NORMAL.value, size=sizeL, style=style)
        ]

        self.saidaL = self.txts[3]

        for txt in self.txts:
            txt.SetForegroundColour((255,255,255))
            txt.SetBackgroundColour((0,0,0))
            jornadaL.Add(txt, 0, wx.ALIGN_CENTER)
        
        size = (x,50)

        self.entrada = gizmos.LEDNumberCtrl(self, -1, size=size)
        self.almoco_start = gizmos.LEDNumberCtrl(self, -1, size=size)
        self.almoco_end = gizmos.LEDNumberCtrl(self, -1, size=size)
        self.saida = gizmos.LEDNumberCtrl(self, -1, size=size)

        jornada = wx.BoxSizer(wx.HORIZONTAL)
        jornada.Add(self.entrada, 1)
        jornada.Add(self.almoco_start, 1)
        jornada.Add(self.almoco_end, 1)
        jornada.Add(self.saida, 1)

        return (jornadaL, jornada)

    def load_info(self):
        self.persistent_info = {}
        try:
            f = open('.\\config.json','r')
            jsontxt = ''.join([x.strip() for x in f.readlines()])
            f.close()
            self.persistent_info = json.loads(jsontxt)
            self.entrada.SetValue(self.persistent_info['entrada'])
            self.almoco_start.SetValue("12:00")
            self.almoco_end.SetValue("13:30")
            self.saida.SetValue("22:20")
            self.OnTimer(None)
        except Exception:
            f = open('.\\config.json','w')
            self.persistent_info['entrada'] = '08:00'
            self.persistent_info['turno1'] = '04:00'
            self.persistent_info['almoco'] = '01:30'
            self.persistent_info['gordura'] = '08:00'
            f.write(json.dumps(self.persistent_info))
            f.close()
            self.load_info()
            pass
        
    def adjust_events(self):
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.entrada.Bind(wx.EVT_LEFT_DCLICK, self.setEntrada1)
        self.saida.Bind(wx.EVT_LEFT_UP, self.changeSaida)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        self.adjust_menu()
        jornadaL, jornada = self.adjust_jornada()
        self.countdown = gizmos.LEDNumberCtrl(self, -1, style=gizmos.LED_ALIGN_CENTER | gizmos.LED_DRAW_FADED)

        lines = wx.BoxSizer(wx.VERTICAL)
        lines.Add(jornadaL, 1, wx.ALIGN_CENTER)
        lines.Add(jornada, 1, wx.ALIGN_CENTER)
        lines.Add(self.countdown, 1, wx.EXPAND)
        self.SetSizer(lines)
        
        self.load_info()
        self.adjust_events()

    def OnTimer(self, evt):
        now = datetime.now().time()
        saida = datetime.strptime(self.saida.Value, '%H:%M').time()
        if now < saida:
            timeleft = datetime.combine(date.today(), saida) - datetime.combine(date.today(), now)
        else:
            timeleft = datetime.combine(date.today(), now) - datetime.combine(date.today(), saida)
            self.countdown.SetForegroundColour(wx.RED)

        st = datetime.strptime(str(timeleft).split('.')[0], "%H:%M:%S").strftime("%H:%M:%S")
        self.countdown.SetValue(st if now < saida else '-' + st)
    
    def OnClose(self, e):
        f = open('.\\config.json','w')
        f.write(json.dumps(self.persistent_info))
        f.close()
        self.Destroy()

    def setEntrada1(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o Horário de entrada no formato hh:mm','Ajustar Horário de Entrada')
        dlg.SetValue('08:00')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^[0-2][0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['entrada']= dlg.GetValue()
                self.entrada.SetValue(self.persistent_info['entrada'])
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_INFORMATION)

    def changeSaida(self, e):
        saidaL = self.saidaL.Label
        if saidaL == self.SaidaStates.NORMAL.value:
            self.saidaL.SetLabel(self.SaidaStates.MIN.value)
            self.saida.SetValue("09:09")
        elif saidaL == self.SaidaStates.MIN.value:
            self.saidaL.SetLabel(self.SaidaStates.MAX.value)
            self.saida.SetValue("11:11")
        else:
            self.saidaL.SetLabel(self.SaidaStates.NORMAL.value)
            self.saida.SetValue("10:10")

    def setGordura(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor de gordura no formato mm:ss','Ajustar Gordura de Saída')
        dlg.SetValue('10:00')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^[0-6][0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['gordura']= dlg.GetValue()
                self.entrada.SetValue(self.persistent_info['gordura'])
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def setTurno1(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor do 1º turno no formato hh:mm','Ajustar horário do 1º turno')
        dlg.SetValue('01:30')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^0[0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['turno1']= dlg.GetValue()
                self.entrada.SetValue(self.persistent_info['turno1'])
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def setAlmoco(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor do horário de almoço no formato hh:mm','Ajustar horário do almoço')
        dlg.SetValue('01:30')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^0[0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['almoco']= dlg.GetValue()
                self.entrada.SetValue(self.persistent_info['almoco'])
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def displayAjuda(self, e):
        wx.MessageBox("txt........", 'Ajuda', wx.OK | wx.ICON_EXCLAMATION)

    def _checkStr(self, txt, pattern):
        return re.compile(pattern).match(txt)