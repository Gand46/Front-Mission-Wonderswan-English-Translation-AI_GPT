-- Natural attract sequence; no input injection, pointer substitution or WRAM edits.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'));local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0;local reads={};local captures={}
local shots={[7500]=13,[8250]=14,[9000]=15,[9750]=16,[10500]=17,[11250]=18,[12000]=19,[12750]=20,[13500]=21,[14250]=22}
emu.addMemoryCallback(function(address,value)
 local idx=math.floor((address-0x49b90)/6)
 if idx>=13 and idx<=22 then reads[idx]=(reads[idx]or 0)+1 end
end,emu.callbackType.read,0x749bde,0x749c19,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addEventCallback(function()
 frame=frame+1
 if shots[frame]then
  local idx=shots[frame];save(string.format('%s/ad_%02d_frame_%05d_NATURAL.png',out,idx,frame),emu.takeScreenshot());captures[#captures+1]=idx
 end
 if frame==10500 then
  local b={};for a=0x6600,0x7fff do b[#b+1]=string.char(emu.read(a,emu.memType.wsMemory))end
  save(out..'/sakata_vram.bin',table.concat(b))
 end
 if frame==15000 then
  local r={};for i=13,22 do r[#r+1]=string.format('"%d":%d',i,reads[i]or 0)end
  save(final,emu.takeScreenshot());save(report,'{"frames":15000,"memory_injection":false,"natural_ad_captures":10,"descriptor_reads":{'..table.concat(r,',')..'}}');emu.stop(0)
 end
end,emu.eventType.endFrame)
