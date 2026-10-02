-- Synthetic QA ROM, not the release ROM. Record 984 tests hard-edge handling.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0;local active=nil;local started=nil;local captures={};local counts={}
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
emu.addMemoryCallback(function(address,value)
 local idx=math.floor((address-0x427C0)/4)
 if idx==983 or idx==984 or idx==955 then
  if active~=idx then active=idx;started=frame end
  counts[idx]=(counts[idx]or 0)+1
 end
end,emu.callbackType.read,0x7427C0,0x745C37,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addEventCallback(function()
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
 if frame>=1220 and frame%20<=2 then t.a=true end
 if started then t.a=(frame-started)>=650 and (frame-started)%650<=2 end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if started and (frame-started)%650==620 then
  save(string.format('%s/stress_%04d_age_%04d_SYNTHETIC.png',out,active,frame-started),emu.takeScreenshot())
  captures[#captures+1]=string.format('{"source":%d,"age":%d}',active,frame-started)
 end
 if frame==9000 then
  save(final,emu.takeScreenshot())
  save(report,'{"frames":9000,"synthetic_ROM":true,"reads_983":'..(counts[983]or 0)..',"reads_984":'..(counts[984]or 0)..',"reads_955":'..(counts[955]or 0)..',"captures":['..table.concat(captures,',')..']}')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
