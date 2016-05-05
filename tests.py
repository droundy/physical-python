import unittest, physical

class TestUnits(unittest.TestCase):
    def test_add(self):
        a = 3*physical.meter
        b = 2*physical.meter
        c = physical.meter*1
        self.assertEqual(a, b+c)
        with self.assertRaises(Exception):
            a + 1
        with self.assertRaises(Exception):
            a + a**2
        with self.assertRaises(Exception):
            1 + a
    def test_sub(self):
        a = 3*physical.meter
        b = 2*physical.meter
        c = physical.meter*1
        self.assertEqual(a-b, c)
        self.assertTrue(physical.has_dimensions(a, physical.meter))
        with self.assertRaises(Exception):
            a - 1
        with self.assertRaises(Exception):
            a - a**2
        with self.assertRaises(Exception):
            1 - a
    def test_pow(self):
        a = 3*physical.meter
        b = 2*physical.meter
        c = physical.meter*1
        self.assertEqual(a*a, a**2)
        self.assertEqual(a*a*a, a**3)
        self.assertEqual(1, a**0)
        with self.assertRaises(Exception):
            a**b
        with self.assertRaises(Exception):
            1**a

if __name__ == '__main__':
    unittest.main()
