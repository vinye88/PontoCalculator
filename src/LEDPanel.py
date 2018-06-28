import wx, json, re
from datetime import datetime, date
from enum import Enum
from PontoCalculator import Jornada
import wx.gizmos as gizmos

class LEDPanel(wx.Frame):
    class SaidaAdvancedMenu(wx.Menu):
        def __init__(self, parent):
            super(type(self), self).__init__()

            self.parent = parent

            self.menu_excesso = wx.MenuItem(self, wx.NewId(), 'Compensar Excesso')
            self.menu_normal = wx.MenuItem(self, wx.NewId(), 'Horário Normal')
            self.menu_ausencia = wx.MenuItem(self, wx.NewId(), 'Compensar Ausência')

            self.Append(self.menu_excesso)
            self.Append(self.menu_normal)
            self.Append(self.menu_ausencia)

            self.Bind(wx.EVT_MENU, self.compensar_excesso, self.menu_excesso)
            self.Bind(wx.EVT_MENU, self.horario_normal, self.menu_normal)
            self.Bind(wx.EVT_MENU, self.compensar_ausencia, self.menu_ausencia)

        def horario_normal(self, e):
            self.parent.update_jornada()

        def compensar_ausencia(self, e):
            dlg = wx.TextEntryDialog(self.parent, 'Entre com o valor da ausência a ser compensada no formato hh:mm','Compensar Ausência')
            dlg.SetValue('00:15')
            if dlg.ShowModal() == wx.ID_OK:
                p = '^0[0-3]:[0-6][0-9]$'
                if self.parent._checkStr(dlg.GetValue(), p):
                    self.parent.current_jornada = self.parent.jornada.compensar_ausencia(self.parent.current_jornada['entrada'],dlg.GetValue())['jornada']
                    self.parent.saidaL.SetLabel(self.parent.SaidaStates.COMP_AUSENCIA.value)
                    self.parent.saida.SetValue(self.parent.current_jornada['saida'])
                    self.parent.OnTimer(None)
                else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

        def compensar_excesso(self, e):
            dlg = wx.TextEntryDialog(self.parent, 'Entre com o valor do excesso a ser compensado no formato hh:mm','Compensar Excesso')
            dlg.SetValue('00:15')
            if dlg.ShowModal() == wx.ID_OK:
                p = '^0[0-3]:[0-6][0-9]$'
                if self.parent._checkStr(dlg.GetValue(), p):
                    self.parent.current_jornada = self.parent.jornada.compensar_excesso(self.parent.current_jornada['entrada'],dlg.GetValue())['jornada']
                    self.parent.saidaL.SetLabel(self.parent.SaidaStates.COMP_EXCESSO.value)
                    self.parent.saida.SetValue(self.parent.current_jornada['saida'])
                    self.parent.OnTimer(None)
                else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    class SaidaStates(Enum):
        MIN             = 'Saída Mínima'
        NORMAL          = 'Saída'
        MAX             = 'Saída Máxima'
        COMP_EXCESSO    = 'Saída com Excesso'
        COMP_AUSENCIA   = 'Saída com Ausência'

    def __init__(self, *args, **kwargs):
        super(LEDPanel, self).__init__(*args, **kwargs)
        self.InitUI()

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

    def adjust_menu(self):
        super(LEDPanel, self).SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        super(LEDPanel, self).SetSize((560,185))
        menubar = wx.MenuBar()

        config_menu = wx.Menu()
        self.config_setalmoco_item = config_menu.Append(wx.NewId(), 'Almoço')
        self.config_setcompensacao_item = config_menu.Append(wx.NewId(), 'Compensação')
        self.config_setturno1_item = config_menu.Append(wx.NewId(), '1º turno')
        self.config_setgordura_item = config_menu.Append(wx.NewId(), 'Gordura')

        menubar.Append(config_menu, '&Configurar')

        ajuda_menu = wx.Menu()
        self.ajuda_sobre = ajuda_menu.Append(-1, 'Sobre')

        menubar.Append(ajuda_menu, '&Ajuda')

        self.SetMenuBar(menubar)

    def adjust_jornada(self):
        jornadaL = wx.BoxSizer(wx.HORIZONTAL)
        x = 135
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

        self.entrada = gizmos.LEDNumberCtrl(self, -1, size=size, style=gizmos.LED_ALIGN_CENTER | gizmos.LED_DRAW_FADED)
        self.almoco_start = gizmos.LEDNumberCtrl(self, -1, size=size, style=gizmos.LED_ALIGN_CENTER | gizmos.LED_DRAW_FADED)
        self.almoco_end = gizmos.LEDNumberCtrl(self, -1, size=size, style=gizmos.LED_ALIGN_CENTER | gizmos.LED_DRAW_FADED)
        self.saida = gizmos.LEDNumberCtrl(self, -1, size=size, style=gizmos.LED_ALIGN_CENTER | gizmos.LED_DRAW_FADED)

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
            if 'entrada' not in self.persistent_info: raise Exception()
            if 'turno1' not in self.persistent_info: raise Exception()
            if 'almoco' not in self.persistent_info: raise Exception()
            if 'gordura' not in self.persistent_info: raise Exception()
            if 'compensacao' not in self.persistent_info: raise Exception()
        except Exception:
            f = open('.\\config.json','w')
            self.persistent_info['entrada'] = '08:00'
            self.persistent_info['turno1'] = '04:00'
            self.persistent_info['almoco'] = '01:30'
            self.persistent_info['gordura'] = '00:18'
            self.persistent_info['compensacao'] = '00:20'
            f.write(json.dumps(self.persistent_info))
            f.close()
            self.load_info()
            pass

        self.update_jornada()
        
    def update_jornada(self):
        self.jornada = Jornada(
            entrada=self.persistent_info['entrada'],
            turno1=self.persistent_info['turno1'],
            almoco=self.persistent_info['almoco'],
            gordura=self.persistent_info['gordura'],
            compensacao=self.persistent_info['compensacao']
        )

        self.current_jornada = self.jornada.calc_jornada()['jornada']
        self.current_jornada['saida'] = self.current_jornada['saida']['normal']

        self.entrada.SetValue(self.current_jornada['entrada'])
        self.almoco_start.SetValue(self.current_jornada['almoco_start'])
        self.almoco_end.SetValue(self.current_jornada['almoco_end'])
        
        self.saidaL.SetLabel(self.SaidaStates.NORMAL.value)
        self.saida.SetValue(self.current_jornada['saida'])
        self.OnTimer(None)

    def adjust_events(self):
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.entrada.Bind(wx.EVT_LEFT_DCLICK, self.setEntrada1)
        self.saida.Bind(wx.EVT_LEFT_UP, self.changeSaida)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.saida.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        self.Bind(wx.EVT_MENU, self.setAlmoco, self.config_setalmoco_item)
        self.Bind(wx.EVT_MENU, self.setCompensacao, self.config_setcompensacao_item)
        self.Bind(wx.EVT_MENU, self.setTurno1, self.config_setturno1_item)
        self.Bind(wx.EVT_MENU, self.setGordura, self.config_setgordura_item)

        self.Bind(wx.EVT_MENU, self.displayAjuda, self.ajuda_sobre)
    
    def OnRightDown(self, e):
        x,y = e.EventObject.GetPosition()
        self.PopupMenu(self.SaidaAdvancedMenu(self), (x+e.x,y+e.y))

    def OnTimer(self, evt):
        now = datetime.now().time()
        saida = datetime.strptime(self.saida.Value, '%H:%M').time()
        if now < saida:
            timeleft = datetime.combine(date.today(), saida) - datetime.combine(date.today(), now)
            self.countdown.SetForegroundColour(wx.GREEN)
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
                self.persistent_info['entrada'] = dlg.GetValue()
                self.update_jornada()
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_INFORMATION)

    def changeSaida(self, e):
        saidaL = self.saidaL.Label
        if saidaL == self.SaidaStates.NORMAL.value:
            self.saidaL.SetLabel(self.SaidaStates.MIN.value)
            self.current_jornada['saida'] = self.jornada.calc_jornada()['jornada']['saida']['limite_inferior']
        elif saidaL == self.SaidaStates.MIN.value:
            self.saidaL.SetLabel(self.SaidaStates.MAX.value)
            self.current_jornada['saida'] = self.jornada.calc_jornada()['jornada']['saida']['limite_superior']
        elif saidaL == self.SaidaStates.MAX.value:
            self.saidaL.SetLabel(self.SaidaStates.NORMAL.value)
            self.current_jornada['saida'] = self.jornada.calc_jornada()['jornada']['saida']['normal']
        self.saida.SetValue(self.current_jornada['saida'])

    def setGordura(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor de gordura no formato mm:ss','Ajustar Gordura de Saída')
        dlg.SetValue('10:00')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^[0-6][0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['gordura']= dlg.GetValue()
                self.update_jornada()
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def setTurno1(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor do 1º turno no formato hh:mm','Ajustar horário do 1º turno')
        dlg.SetValue('01:30')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^0[0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['turno1']= dlg.GetValue()
                self.update_jornada()
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def setAlmoco(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor do horário de almoço no formato hh:mm','Ajustar horário do almoço')
        dlg.SetValue('01:30')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^0[0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['almoco']= dlg.GetValue()
                self.update_jornada()
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def setCompensacao(self, e):
        dlg = wx.TextEntryDialog(self, 'Entre com o valor do horário de compensação no formato hh:mm','Ajustar horário de Compensação')
        dlg.SetValue('00:20')
        if dlg.ShowModal() == wx.ID_OK:
            p = '^0[0-9]:[0-6][0-9]$'
            if self._checkStr(dlg.GetValue(), p):
                self.persistent_info['compensacao']= dlg.GetValue()
                self.update_jornada()
            else: wx.MessageBox("Valor errado!", 'Info', wx.OK | wx.ICON_EXCLAMATION)

    def displayAjuda(self, e):
        txt = 'Comandos básicos do Ponto Calculator\n\n'
        txt += 'Utilize o menu Configurar para ajustar horário de almoço, gordura, 1º turno e compensaçao.\n\n'
        txt += 'Clique duplo c/ botão esquerdo no display da entrada: Ajustar entrada.\n\n'
        txt += 'Clique simples c/ botão esquerdo no display de saída: Troca entre Saída normal, Saída Mínima e Saída Máxima.\n\n'
        txt += 'Clique simples c/ botão direito no display de saída: Abre menu p/ configurar a saída com excesso, ausência ou horário normal.\n\n'
        wx.MessageBox(txt, 'Ajuda', wx.OK | wx.ICON_INFORMATION)

    def _checkStr(self, txt, pattern):
        return re.compile(pattern).match(txt)