import unittest
from build_v032 import apply_ips,make_ips,label_pixels,decode_pixels,encode_pixels,build

class BuildTests(unittest.TestCase):
    def test_bad_base_rejected(self):
        with self.assertRaises(ValueError):build(b'bad',{})
    def test_patch_roundtrip(self):
        a=b'abcdef';b=b'aBCdEf';self.assertEqual(apply_ips(a,make_ips(a,b)),b)
    def test_empty_patch(self):self.assertEqual(apply_ips(b'abc',make_ips(b'abc',b'abc')),b'abc')
    def test_rle(self):self.assertEqual(apply_ips(b'abcdef',b'PATCH\x00\x00\x01\x00\x00\x00\x03ZEOF'),b'aZZZef')
    def test_truncated_patch(self):
        with self.assertRaises(ValueError):apply_ips(b'abc',b'PATCH')
    def test_invalid_header(self):
        with self.assertRaises(ValueError):apply_ips(b'abc',b'NOTPATCH')
    def test_patch_bounds(self):
        with self.assertRaises(ValueError):apply_ips(b'abc',b'PATCH\x00\x00\x03\x00\x01ZEOF')
    def test_pixel_roundtrip(self):
        a=[[((x*3+y)%16) for x in range(16)] for y in range(16)]
        self.assertEqual(decode_pixels(encode_pixels(a)),a)
    def test_glyphs_fit_advance(self):
        for label in ['DF','AT','WT','PW','AM','AC','MV','ML','SR','LR','R','G','E','V','A','P']:
            a=decode_pixels(label_pixels(label));self.assertTrue(all(v==6 for row in a for v in row[8:]))
    def test_eof_reserved_offset(self):
        a=bytearray(0x454F48);b=bytearray(a);b[0x454F46]=1
        self.assertEqual(apply_ips(a,make_ips(a,b)),b)

if __name__=='__main__':unittest.main()
