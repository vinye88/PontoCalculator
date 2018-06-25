import unittest

from PontoCalculator import Jornada

class TestJornada(unittest.TestCase):
    hs=[
            ['08:00','18:20'],
            ['07:21','18:13'],
            ['07:24','18:25'],
            ['07:00','17:00'],
            ['07:41','18:11'],
            ['07:17','17:37']
    ]

    def test_calc_jornada(self):
        self.assertEqual(str(Jornada(self.hs[0][0]).calc_jornada()), "{'jornada': {'entrada': '08:00', 'almoco_start': '12:00', 'almoco_end': '13:30', 'saida': {'limite_inferior': '18:10', 'normal': '18:20', 'limite_superior': '18:48'}}}")
        self.assertEqual(str(Jornada(self.hs[1][0]).calc_jornada()), "{'jornada': {'entrada': '07:21', 'almoco_start': '11:21', 'almoco_end': '12:51', 'saida': {'limite_inferior': '17:31', 'normal': '17:41', 'limite_superior': '18:09'}}}")
        self.assertEqual(str(Jornada(self.hs[2][0]).calc_jornada()), "{'jornada': {'entrada': '07:24', 'almoco_start': '11:24', 'almoco_end': '12:54', 'saida': {'limite_inferior': '17:34', 'normal': '17:44', 'limite_superior': '18:12'}}}")
        self.assertEqual(str(Jornada(self.hs[3][0]).calc_jornada()), "{'jornada': {'entrada': '07:00', 'almoco_start': '11:00', 'almoco_end': '12:30', 'saida': {'limite_inferior': '17:10', 'normal': '17:20', 'limite_superior': '17:48'}}}")
        self.assertEqual(str(Jornada(self.hs[4][0]).calc_jornada()), "{'jornada': {'entrada': '07:41', 'almoco_start': '11:41', 'almoco_end': '13:11', 'saida': {'limite_inferior': '17:51', 'normal': '18:01', 'limite_superior': '18:29'}}}")
        self.assertEqual(str(Jornada(self.hs[5][0]).calc_jornada()), "{'jornada': {'entrada': '07:17', 'almoco_start': '11:17', 'almoco_end': '12:47', 'saida': {'limite_inferior': '17:27', 'normal': '17:37', 'limite_superior': '18:05'}}}")

    def test_calc_check_jornada(self):
        self.assertEqual(str(Jornada(self.hs[0][0]).check_jornada(self.hs[0][0], self.hs[0][1])), "{'jornada_valida': True}")
        self.assertEqual(str(Jornada(self.hs[1][0]).check_jornada(self.hs[1][0], self.hs[1][1])), "{'jornada_valida': False, 'excesso': '00:14'}")
        self.assertEqual(str(Jornada(self.hs[2][0]).check_jornada(self.hs[2][0], self.hs[2][1])), "{'jornada_valida': False, 'excesso': '00:23'}")
        self.assertEqual(str(Jornada(self.hs[3][0]).check_jornada(self.hs[3][0], self.hs[3][1])), "{'jornada_valida': False, 'ausencia': '00:38'}")
        self.assertEqual(str(Jornada(self.hs[4][0]).check_jornada(self.hs[4][0], self.hs[4][1])), "{'jornada_valida': True}")
        self.assertEqual(str(Jornada(self.hs[5][0]).check_jornada(self.hs[5][0], self.hs[5][1])), "{'jornada_valida': True}")

    def test_compensar_ausencia(self):
        self.assertEqual(str(Jornada().compensar_ausencia('08:00', '00:09')),"{'jornada': {'entrada': '08:00', 'almoco_start': '12:00', 'almoco_end': '13:30', 'saida': '18:49'}}")
        self.assertEqual(str(Jornada().compensar_ausencia('08:00', '00:12')),"{'jornada': {'entrada': '08:00', 'almoco_start': '12:00', 'almoco_end': '13:30', 'saida': '18:39'}}")

    def test_compensar_excesso(self):
        self.assertEqual(str(Jornada().compensar_excesso('08:00', '00:09')),"{'jornada': {'entrada': '08:00', 'almoco_start': '12:00', 'almoco_end': '13:30', 'saida': '17:51'}}")
        self.assertEqual(str(Jornada().compensar_excesso('08:00', '00:12')),"{'jornada': {'entrada': '08:00', 'almoco_start': '12:00', 'almoco_end': '13:30', 'saida': '17:50'}}")

if __name__ == '__main__':
    unittest.main()