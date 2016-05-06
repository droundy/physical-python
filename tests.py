import unittest

from physical import *

class TestUnits(unittest.TestCase):
    def test_add(self):
        a = 3*meter
        b = 2*meter
        c = meter*1
        self.assertEqual(a, b+c)
        with self.assertRaises(Exception):
            a + 1
        with self.assertRaises(Exception):
            a + a**2
        with self.assertRaises(Exception):
            1 + a
        a = vector(0,1,2)*meter
        b = vector(2,1,0)*meter
        c = vector(2,2,2)*meter
        self.assertEqual(a+b,c)
    def test_sub(self):
        a = 3*meter
        b = 2*meter
        c = meter*1
        self.assertEqual(a-b, c)
        self.assertTrue(has_dimensions(a, meter))
        with self.assertRaises(Exception):
            a - 1
        with self.assertRaises(Exception):
            a - a**2
        with self.assertRaises(Exception):
            1 - a
    def test_pow(self):
        a = 3*meter
        b = 2*meter
        c = meter*1
        self.assertEqual(a*a, a**2)
        self.assertEqual(a*a*a, a**3)
        self.assertEqual(1, a**0)
        with self.assertRaises(Exception):
            a**b
        with self.assertRaises(Exception):
            1**a

if __name__ == '__main__':
    unittest.main()
