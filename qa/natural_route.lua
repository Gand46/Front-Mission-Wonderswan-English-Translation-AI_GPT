local ranges={
{'nested_3317',8175908,8175923},
{'nested_3339',8177036,8177073},
{'pointer_pattern_1BA954',1812820,1812823},
{'pointer_pattern_53D87E',5494910,5494913},
{'pointer_pattern_74028D',7602829,7602832},
{'pointer_pattern_740611',7603729,7603732},
{'pointer_pattern_740617',7603735,7603738},
{'pointer_pattern_7406D7',7603927,7603930},
{'pointer_pattern_7407C7',7604167,7604170},
{'pointer_pattern_7408B7',7604407,7604410},
{'pointer_pattern_750129',7668009,7668012},
{'pointer_pattern_750292',7668370,7668373},
{'pointer_pattern_75B235',7713333,7713336},
{'pointer_pattern_75E8D3',7727315,7727318},
{'pointer_pattern_75EA9B',7727771,7727774},
{'pointer_pattern_75F53C',7730492,7730495},
{'pointer_pattern_763195',7745941,7745944},
{'pointer_pattern_776BE3',7826403,7826406},
{'pointer_pattern_779994',7838100,7838103},
{'pointer_pattern_779A26',7838246,7838249},
{'pointer_pattern_77B85E',7845982,7845985},
{'pointer_pattern_77BD0C',7847180,7847183},
{'pointer_pattern_77BE78',7847544,7847547},
{'pointer_pattern_7F6544',8348996,8348999},
{'retained_start_7B0001',8060929,8060930},
{'retained_start_7B00AA',8061098,8061099},
{'retained_start_7B023E',8061502,8061503},
{'retained_start_7B02A9',8061609,8061610},
{'retained_start_7B0406',8061958,8061959},
{'retained_start_7B141E',8066078,8066079},
{'retained_start_7CA236',8167990,8167991},
{'retained_start_7CA77E',8169342,8169343},
{'retained_start_7CA847',8169543,8169544},
{'retained_start_7CA873',8169587,8169588},
{'retained_start_7CA8A9',8169641,8169642},
{'retained_start_7CA8DC',8169692,8169693},
}
local MODE="route"
local FRAMES=24000
-- Bounded natural boot/attract or new-game inputs; no ROM/WRAM mutation.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0;local events={};local main={};local gfx={};local observed={}
for _,q in ipairs(ranges)do
 emu.addMemoryCallback(function(address,value)
  local t=observed[q[1]]
  if not t then
   local s=emu.getState();t={count=0,frame=frame,cs=s['cpu.cs'],ip=s['cpu.ip'],address=address};observed[q[1]]=t
  end
  t.count=t.count+1
 end,emu.callbackType.read,q[2],q[3],emu.cpuType.ws,emu.memType.wsPrgRom)
end
emu.addMemoryCallback(function(address,value)
 local i=math.floor(((address%65536)-0x27c0)/4)
 if i>=0 and i<3358 then main[i]=(main[i]or 0)+1 end
end,emu.callbackType.read,0x7427c0,0x745c37,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addMemoryCallback(function(address,value)
 local i=math.floor(((address%65536)-0x9b90)/6)
 if i>=0 and i<1616 then gfx[i]=(gfx[i]or 0)+1 end
end,emu.callbackType.read,0x749b90,0x74c16f,emu.cpuType.ws,emu.memType.wsPrgRom)
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
emu.addEventCallback(function()
 if MODE~='route' then return end
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
 if frame>=1220 and frame<FRAMES and frame%20<=2 then t.a=true end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
local function counts(t)
 local a={};for k,v in pairs(t)do a[#a+1]=string.format('"%d":%d',k,v)end;return '{'..table.concat(a,',')..'}'
end
emu.addEventCallback(function()
 frame=frame+1
 if frame%3000==0 then save(string.format('%s/frame_%05d.png',out,frame),emu.takeScreenshot())end
 if frame==FRAMES then
  local a={}
  for _,q in ipairs(ranges)do
   local t=observed[q[1]]
   if t then a[#a+1]=string.format('"%s":{"reads":%d,"first_frame":%d,"cs":%d,"ip":%d,"cpu_address":%d}',q[1],t.count,t.frame,t.cs,t.ip,t.address)
   else a[#a+1]=string.format('"%s":{"reads":0}',q[1]) end
  end
  local data='{"mode":"'..MODE..'","frames":'..frame..',"memory_injection":false,"ranges":{'..table.concat(a,',')..'},"main_table":'..counts(main)..',"graphics_descriptors":'..counts(gfx)..'}'
  save(out..'/coverage.json',data);save(final,emu.takeScreenshot());save(report,data);emu.stop(0)
 end
end,emu.eventType.endFrame)
