-- FC dynamic name and FD glyph regression.
-- Controlled pointer injection into introductory secondary-renderer dialogue.
-- This is NOT a natural replay of the Olson scene.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local cases={
 [983]={target=956,old={209,121,0,176},new={18,109,0,192}},
 [984]={target=545,old={153,189,0,176},new={185,16,0,192}},
}
local frame=0;local active=nil;local started=nil;local reads={};local samples={}
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
emu.addMemoryCallback(function(address,value)
 local idx=math.floor((address-0x427C0)/4);local c=cases[idx]
 if not c then return end
 local n=(address-0x427C0)%4+1;local replacement=nil
 if value==c.old[n]then replacement=c.new[n]
 elseif n<4 and value==c.old[n]+256*c.old[n+1]then replacement=c.new[n]+256*c.new[n+1]
 else save(out..'/callback_mismatch.txt',address..' '..value);emu.stop(2);return end
 if active~=idx then active=idx;started=frame end
 reads[idx]=(reads[idx]or 0)+1
 return replacement
end,emu.callbackType.read,0x7427C0,0x745C37,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addEventCallback(function()
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
 if frame>=1220 and frame%20<=2 then t.a=true end
 if started then t.a=(frame-started)>=500 and (frame-started)%500<=2 end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if started and (frame-started)%500==480 then
  save(string.format('%s/record_%04d_age_%04d_CONTROLLED.png',out,cases[active].target,frame-started),emu.takeScreenshot())
  local seg=emu.read(0x3fb8,emu.memType.wsMemory)+256*emu.read(0x3fb9,emu.memType.wsMemory)
  local off=emu.read(0x3fba,emu.memType.wsMemory)+256*emu.read(0x3fbb,emu.memType.wsMemory)
  samples[#samples+1]=string.format('{"target":%d,"frame":%d,"secondary_segment":%d,"secondary_offset":%d}',cases[active].target,frame,seg,off)
 end
 if frame==8000 then
  save(final,emu.takeScreenshot())
  save(report,'{"frames":8000,"pointer_injection":true,"reads_983":'..(reads[983]or 0)..',"reads_984":'..(reads[984]or 0)..',"samples":['..table.concat(samples,',')..']}')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
