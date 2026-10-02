"""Generate reproducible controlled/synthetic variants, not new translations."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=(ROOT/'reported_secondary.lua').read_text()
source=source.replace('target=2817,old={209,121,0,176},new={64,111,0,192}',
                      'target=956,old={209,121,0,176},new={18,109,0,192}')
source=source.replace('target=2821,old={153,189,0,176},new={209,251,0,240}',
                      'target=545,old={153,189,0,176},new={185,16,0,192}')
(ROOT/'secondary_controls.lua').write_text('-- FC dynamic name and FD glyph regression.\n'+source)
source=(ROOT/'stress.lua').read_text()
source=source.replace('frame=frame+1','''frame=frame+1
 -- Force the existing narrow-width mode after record initialization.
 -- SYNTHETIC capacity branch test, NOT a naturally reached narrow window.
 if active==983 and frame-started==2 then
  emu.write(0x3fce,0,emu.memType.wsMemory)
  if emu.read(0x3fce,emu.memType.wsMemory)~=0 then emu.stop(2) end
 end''')
source=source.replace('"synthetic_ROM":true','"synthetic_ROM":true,"forced_narrow_mode":true')
(ROOT/'stress_narrow.lua').write_text(source)
