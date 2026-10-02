local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0
emu.addEventCallback(function()
 frame=frame+1
 if frame%1500==0 then
  save(string.format('%s/idle_%05d.png',out,frame),emu.takeScreenshot())
 end
 if frame==18000 then
  local b={};for a=0,65535 do b[#b+1]=string.char(emu.read(a,emu.memType.wsMemory))end
  save(out..'/wram.bin',table.concat(b))
  local s={};for k,v in pairs(emu.getState())do s[#s+1]=tostring(k)..'='..tostring(v)end
  save(out..'/state.txt',table.concat(s,'\n'))
  save(final,emu.takeScreenshot());save(report,'{"frames":18000,"injection":false}')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
