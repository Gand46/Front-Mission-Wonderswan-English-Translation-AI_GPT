import unittest
from resources import decode,encode
class RLETests(unittest.TestCase):
 def test_cpu_opcode_vectors(self):
  cases=[('770077777788779977aa77bb77cc77dd77eeee',bytes.fromhex('00778899aabbccddee')),
   ('bb03ee',b'\0'*3),('cc03ee',b'\xff'*3),('dd045aee',b'Z'*4),
   ('88034142ee',b'AB'*3),('994142ee',b'AB'*2),('aa03feffee',bytes.fromhex('feffffff0000'))]
  for s,want in cases:
   raw=bytes.fromhex(s);got,end=decode(raw,0);self.assertEqual(got,want);self.assertEqual(end,len(raw))
 def test_encoder_escaped_bytes_and_repeats(self):
  for b in [bytes(range(256)),bytes(range(255,-1,-1)),b'\xee'*600,b'AB'*270,b'\0'*1000,b'\xff'*1000,bytes.fromhex('feffffff00000100')]:
   with self.subTest(length=len(b)):self.assertEqual(decode(encode(b),0)[0],b)
if __name__=='__main__':unittest.main()
