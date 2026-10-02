-- Authorized bounded headless QA; no ROM/WRAM modifications.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local frame=0
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
local checkpoints={}
for _,f in ipairs({500,550,900,1230,1348,1600,2000,3000,4000,8000,12000,16000,18500,20000,24000})do checkpoints[f]=true end
emu.addEventCallback(function()
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
 if frame>=1220 and frame<24000 and frame%20<=2 then t.a=true end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if checkpoints[frame]then save(string.format('%s/frame_%05d.png',out,frame),emu.takeScreenshot()) end
 if frame==24000 then
  save(final,emu.takeScreenshot())
  save(report,'{"lua_frames":24000,"checkpoints":15,"route_completed":true,"gameplay_assertions":false,"memory_injection":false}\n')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
