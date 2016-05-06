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
    def test_sqrt(self):
        b = 4*meter
        self.assertEqual(sqrt(b)**2, b)
    def test_division(self):
        a = 2*meter
        b = 4*meter
        self.assertEqual(b/a, 2)
        self.assertEqual(a/b, 0.5)
        v = vector(1,2,3)*second
        self.assertEqual(v/a, vector(0.5,1,1.5)*second/meter)
        with self.assertRaises(Exception):
            a/v
        with self.assertRaises(Exception):
            v/v
    def test_mul(self):
        a = 2*meter
        b = 4*meter
        self.assertEqual(b*a, 8*meter**2)
        v = vector(1,2,3)*second
        vv = second*vector(1,2,3)
        self.assertEqual(vector(0,0,0).mks, (0,0,0))
        self.assertEqual(v.mks, (0,0,1))
        self.assertEqual(v,vv)
        self.assertEqual(v*a, vector(2,4,6)*second*meter)
        self.assertEqual(a*v, vector(2,4,6)*second*meter)
        with self.assertRaises(Exception):
            v*v
        self.assertEqual(v.x, 1*second)
        with self.assertRaises(Exception):
            a = vector(0,0,0)*meter
            a.x + 3
    def test_value(self):
        self.assertEqual(value(3*meter), 3)
        self.assertEqual(value(3.0*meter), 3.0)
    def test_xsetter(self):
        v = vector(2,2,2)*meter
        self.assertEqual(v.x, 2*meter)
        v.x = 3*meter
        self.assertEqual(v.x, 3*meter)
        with self.assertRaises(Exception):
            v.x = 3
    def test_ysetter(self):
        v = vector(2,2,2)*meter
        self.assertEqual(v.y, 2*meter)
        v.y = 3*meter
        self.assertEqual(v.y, 3*meter)
        with self.assertRaises(Exception):
            v.y = 3
    def test_zsetter(self):
        v = vector(2,2,2)*meter
        self.assertEqual(v.z, 2*meter)
        v.z = 3*meter
        self.assertEqual(v.z, 3*meter)
        with self.assertRaises(Exception):
            v.z = 3

if __name__ == '__main__':
    unittest.main()
