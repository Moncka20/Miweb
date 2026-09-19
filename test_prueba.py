import unittest

from Prueba import multiplicar, sumar, resta


class PruebaOperaciones(unittest.TestCase):
    def test_sumar(self):
        self.assertEqual(sumar(2, 3), 5)

    def test_resta(self):
        self.assertEqual(resta(5, 3), 2)

    def test_multiplicar(self):
        self.assertEqual(multiplicar(4, 3), 12)


if __name__ == "__main__":
    unittest.main()