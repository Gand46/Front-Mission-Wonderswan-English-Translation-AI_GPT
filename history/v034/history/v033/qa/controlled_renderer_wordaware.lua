-- Controlled pointer-read substitution, NOT natural gameplay coverage.
-- Values are verified byte-by-byte against this exact ROM before substitution.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local cases={
 [955]={target=137,old={3,245,0,192},new={95,35,0,192}},
 [956]={target=138,old={18,109,0,192},new={34,44,0,192}},
 [957]={target=139,old={7,245,0,240},new={198,194,0,208}},
 [958]={target=496,old={184,93,0,192},new={62,77,0,192}},
 [959]={target=545,old={210,242,0,240},new={185,16,0,192}},
 [960]={target=486,old={8,144,0,208},new={168,230,0,208}},
 [961]={target=1011,old={211,143,0,176},new={0,0,0,192}},
 [962]={target=2099,old={211,197,0,176},new={31,15,0,192}},
}
local frame=0;local active=nil;local started=nil;local done={};local reads={};local glyphs={}
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
emu.addMemoryCallback(function(address,value)
 assert(address>=0x427C0 and address<=0x45C37,'Unexpected CPU mapping')
 local idx=math.floor((address-0x427C0)/4);local c=cases[idx]
 if c then
  local n=(address-0x427C0)%4+1
  local replacement=nil
  if value==c.old[n] then replacement=c.new[n]
  elseif n<4 and value==c.old[n]+256*c.old[n+1] then replacement=c.new[n]+256*c.new[n+1]
  else
   save(out..'/callback_mismatch.json',string.format('{"address":%d,"value":%d,"index":%d,"byte":%d}',address,value,idx,n))
   emu.stop(2);return
  end
  if active~=idx then active=idx;started=frame end
  reads[idx]=(reads[idx]or 0)+1
  return replacement
 end
end,emu.callbackType.read,0x7427C0,0x745C37,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addMemoryCallback(function(address,value)
 local gid=math.floor(((address%65536)-0xE000)/128)+0x40
 glyphs[gid]=(glyphs[gid]or 0)+1
end,emu.callbackType.read,0x26E080,0x26EAFF,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addEventCallback(function()
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
 if frame>=1220 and frame%20<=2 then t.a=true end
 if started and frame-started<500 then t.a=false end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if started and frame-started==480 then
  save(string.format('%s/record_%04d_CONTROLLED.png',out,cases[active].target),emu.takeScreenshot())
  done[active]=true
 end
 local count=0;for k in pairs(done)do count=count+1 end
 if count==8 or frame==18000 then
  local gs={};for k,v in pairs(glyphs)do gs[#gs+1]=string.format('"C6:%02X":%d',k,v)end
  local cs={};for k,c in pairs(cases)do cs[#cs+1]=string.format('{"source":%d,"target":%d,"reads":%d,"captured":%s}',k,c.target,reads[k]or 0,tostring(done[k]or false))end
  save(final,emu.takeScreenshot())
  save(report,'{"lua_frames":'..frame..',"controlled_pointer_substitution":true,"rom_file_modified":false,"cases":['..table.concat(cs,',')..'],"glyph_read_counts":{'..table.concat(gs,',')..'}}\n')
  emu.stop(count==8 and 0 or 1)
 end
end,emu.eventType.endFrame)
