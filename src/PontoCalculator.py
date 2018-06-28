
import datetime, wx, time
import wx.gizmos as gizmos

class Jornada():
    def calc_jornada(self):
        almoco_start, almoco_end = self._calcular_almoco(self.entrada)
        saida = almoco_end + (self.jornada - self.turno1)
        return {
            'jornada':{
                'entrada':self._p(self.entrada),
                'almoco_start':self._p(almoco_start),
                'almoco_end': self._p(almoco_end),
                'saida':{
                    'limite_inferior':self._p(saida - self.limite),
                    'normal':self._p(saida),
                    'limite_superior':self._p(saida + self.limite + self.gordura)
                }
            }
        }

    def check_jornada(self, entrada, saida):
        status = {}
        jornada_calc = self._d(saida) - self._d(entrada) - self.almoco
        if self._check_limite_jornada(jornada_calc):
            status['jornada_valida'] = True
        else:
            status['jornada_valida'] = False
            if jornada_calc < self.jornada:
                devendo = self.jornada - jornada_calc + self.gordura
                status['ausencia'] = self._p(devendo)
            else:
                sobrando = jornada_calc - self.jornada - self.gordura
                status['excesso'] = self._p(sobrando)
        return status

    def compensar_excesso(self, entrada, excesso):
        almoco_start, almoco_end = self._calcular_almoco(self._d(entrada))
        saida = almoco_end + (self.jornada - self.turno1) - self.gordura - (self.limite + self._d('00:01'))
        if self._d(excesso) > (self.limite + self._d('00:01')):
            saida -= self._d(excesso) - (self.limite + self._d('00:01'))
        return {
            'jornada':{
                'entrada':self._p(self._d(entrada)),
                'almoco_start':self._p(almoco_start),
                'almoco_end': self._p(almoco_end),
                'saida':self._p(saida)
            }
        }

    def compensar_ausencia(self, entrada, ausencia):
        almoco_start, almoco_end = self._calcular_almoco(self._d(entrada))
        saida = almoco_end + (self.jornada - self.turno1) + self.gordura
        saida += (self.limite + self._d('00:01')) if self._d(ausencia) <= (self.limite + self._d('00:01')) else self._d(ausencia)
        return {
            'jornada':{
                'entrada':self._p(self._d(entrada)),
                'almoco_start':self._p(almoco_start),
                'almoco_end': self._p(almoco_end),
                'saida':self._p(saida)
            }
        }
    
    def _check_limite_jornada(self, jornada_calc):
        jornada_calc_inf = self.jornada - self.limite
        jornada_calc_sup = self.jornada + self.limite + self.gordura
        if jornada_calc >= jornada_calc_inf and jornada_calc <= jornada_calc_sup: return True
        else: return False

    def _calcular_almoco(self, entrada):
        return (
            entrada + self.turno1,
            entrada + self.turno1 + self.almoco
        )

    def _p(self, _time):
        try: return ':'.join([x.rjust(2,'0') for x in str(self._d(_time)).split(':')[:2]])
        except: return ':'.join([x.rjust(2,'0') for x in str(_time).split(':')[:2]])

    def _d(self, _time):
        return datetime.timedelta(hours=int(_time.split(':')[0]),minutes=int(_time.split(':')[1]))

    def __init__(self, entrada='00:00', jornada='08:30', almoco='01:30', turno1 = '04:00', compensacao='00:20', limite='00:10', gordura='00:18'):
        self.entrada = self._d(entrada)
        self.jornada = self._d(jornada) + self._d(compensacao)
        self.almoco = self._d(almoco)
        self.turno1 = self._d(turno1)
        self.compensacao = self._d(compensacao)
        self.limite = self._d(limite)
        self.gordura = self._d(gordura)
