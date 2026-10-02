-- Synthetic pointer substitution into the existing primary renderer.
-- This does NOT identify or exercise the native ending-scene list consumer.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'));local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0;local active=nil;local started=nil;local done={};local reads={};local initialized=false
local function rd(p)return emu.read(p,emu.memType.wsMemory)end
local function word(p)return rd(p)+256*rd(p+1)end
local function far(index)local p=0x427c0+index*4;return word(p)+16*word(p+2),word(p+2)end
local function fail(s)save(out..'/FAIL.txt',s);emu.stop(2)end
local function init()
 if MODE=='repaired' then
  for _,q in ipairs({{3317,7},{3339,18}})do
   local p=far(q[1]);for n=0,q[2]-1 do if word(p+n*2)==65535 then fail('Early list terminator');return end end
   if word(p+q[2]*2)~=65535 then fail('Missing list terminator');return end
  end
 end
 for source,c in pairs(cases)do
  local p,seg=far(c.index)
  if MODE=='repaired' and c.table~=0 then local root,s=far(c.table);seg=s;p=seg*16+word(root+c.child*2)end
  for j,v in ipairs(c.payload)do if rd(p+j-1)~=v then fail('Payload mismatch '..c.index);return end end
  local off=p-seg*16;c.new={off%256,math.floor(off/256),seg%256,math.floor(seg/256)};c.cpu_target=p
 end
 initialized=true
end
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
emu.addMemoryCallback(function(address,value)
 local idx=math.floor(((address%65536)-0x27c0)/4);local c=cases[idx]
 if c and initialized then
  local n=((address%65536)-0x27c0)%4+1;local replacement
  if value==c.old[n] then replacement=c.new[n]
  elseif n<4 and value==c.old[n]+256*c.old[n+1] then replacement=c.new[n]+256*c.new[n+1]
  else fail('Pointer read mismatch '..idx);return end
  if active~=idx then active=idx;started=frame end
  reads[idx]=(reads[idx]or 0)+1;return replacement
 end
end,emu.callbackType.read,0x7427c0+955*4,0x7427c0+963*4-1,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addEventCallback(function()
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
 if frame>=1220 and frame%20<=2 then t.a=true end
 if started and frame-started<400 then t.a=false end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==200 then init()end
 if started and frame-started==380 then
  save(string.format('%s/record_%04d_CONTROLLED.png',out,cases[active].index),emu.takeScreenshot());done[active]=true
 end
 local count=0;local total=0;for k in pairs(cases)do total=total+1;if done[k]then count=count+1 end end
 if count==total or frame==20000 then
  local rows={}
  for k,c in pairs(cases)do rows[#rows+1]=string.format('{"source":%d,"target":%d,"pointer_reads":%d,"captured":%s,"cpu_target":%d}',k,c.index,reads[k]or 0,tostring(done[k]or false),c.cpu_target or 0)end
  save(final,emu.takeScreenshot());save(report,'{"group":"'..GROUP..'","mode":"'..MODE..'","frames":'..frame..',"pointer_injection":true,"native_ending_consumer":false,"memory_payloads_verified":'..tostring(initialized)..',"captured":'..count..',"expected":'..total..',"cases":['..table.concat(rows,',')..']}');emu.stop(count==total and 0 or 1)
 end
end,emu.eventType.endFrame)
