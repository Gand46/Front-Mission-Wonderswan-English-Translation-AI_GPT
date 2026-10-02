import unittest
from audit_japanese import parse,nested,ONE,JP_LABEL_CODES

class AuditTests(unittest.TestCase):
    def test_production_lowercase(self):
        self.assertEqual(parse(bytes([0x37,0x38,0xbb,0xff,0]),0,{})['text'],'ab {END}')
    def test_japanese_preserved(self):
        self.assertEqual(parse(bytes([0x12,0x0c,0x13,0xff,0]),0,{b'\x12':'て',b'\x0c':'す',b'\x13':'と'})['text'],'てすと{END}')
    def test_ff_trail_not_terminator(self):
        r=parse(bytes.fromhex('c2 ff 37 ff 00'),0,{})
        self.assertEqual(r['length'],4);self.assertEqual(r['text'],'{C2:FF}a{END}')
    def test_ff_control_parameter_not_terminator(self):
        self.assertEqual(parse(bytes.fromhex('f9 ff 37 ff 00'),0,{})['length'],4)
    def test_c8_supported(self):
        self.assertEqual(parse(bytes.fromhex('c8 ff 37 ff 00'),0,{})['length'],4)
    def test_fd_special(self):
        self.assertEqual(parse(bytes.fromhex('fd 2c ff 00'),0,{})['japanese'],[])
    def test_near_pointer_table(self):
        self.assertEqual(nested(bytes.fromhex('08000a000c00ffff0000000000000000'),0),[8,10,12])
    def test_reject_text_as_table(self):
        self.assertIsNone(nested(b'\x00'*258,0))
    def test_expected_mapping_sizes(self):
        self.assertEqual(len(ONE),30);self.assertEqual(len(JP_LABEL_CODES),16)

if __name__=='__main__':unittest.main()
