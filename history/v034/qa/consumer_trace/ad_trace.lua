local final=assert(os.getenv('MESEN_CAPTURE_PATH'));local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0;local reads={};local pcs={};local events={}
local function dump(f)
 local b={};for a=0,65535 do b[#b+1]=string.char(emu.read(a,emu.memType.wsMemory))end
 save(string.format('%s/wram_%05d.bin',out,f),table.concat(b))
 local s={};for k,v in pairs(emu.getState())do s[#s+1]=tostring(k)..'='..tostring(v)end
 save(string.format('%s/state_%05d.txt',out,f),table.concat(s,'\n'))
end
emu.addMemoryCallback(function(address,value)
 if frame<9000 or frame>10600 then return end
 -- Count graphics bank reads; query full state only once per CPU 256-byte block per frame.
 local key=frame..':'..math.floor(address/256)
 if not reads[key]then
  local s=emu.getState()
  reads[key]={frame,address,s['cpu.cs'],s['cpu.ip'],s['cart.selectedBanks0'],s['cart.selectedBanks1'],s['cart.selectedBanks2'],s['cart.selectedBanks3']}
 end
end,emu.callbackType.read,0,0x6fffff,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=6800 and frame%200==0 then save(string.format('%s/ad_%05d.png',out,frame),emu.takeScreenshot())end
 if frame==9000 or frame==10500 then dump(frame)end
 if frame==14000 then
  local rows={};for k,v in pairs(reads)do local a={};for _,n in ipairs(v)do a[#a+1]=tostring(n)end;rows[#rows+1]=table.concat(a,',')end
  save(out..'/reads.csv','frame,address,cs,ip,bank0,bank1,bank2,bank3\n'..table.concat(rows,'\n'))
  save(final,emu.takeScreenshot());save(report,'{"frames":14000,"injection":false}');emu.stop(0)
 end
end,emu.eventType.endFrame)
