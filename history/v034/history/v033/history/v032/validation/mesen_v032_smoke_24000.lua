-- Mesen 2.1.1, normal GUI. Open through Script Window after loading the ROM.
-- Set this to a NEW EXISTING directory before running. No deletion is performed.
local out = 'CHANGE_TO_EXISTING_OUTPUT_DIRECTORY'
assert(out ~= 'CHANGE_TO_EXISTING_OUTPUT_DIRECTORY', 'Set output directory first')
local function save(path, bytes)
  local f=assert(io.open(path,'wb'));f:write(bytes);f:close()
end
save(out..'/started.txt','v0.32-TEST route started; no PASS is implied\n')
local frame=0
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
local capture={}
for _,f in ipairs({500,550,900,1230,1348,1600,2000,3000,4000,8000,12000,16000,18500,20000,24000}) do capture[f]=true end
emu.addEventCallback(function()
  local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
  for _,p in ipairs(route) do if frame>=p[1] and frame<=p[2] then t[p[3]]=true end end
  if frame>=1220 and frame<24000 and frame%20<=2 then t.a=true end
  emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if capture[frame] then save(string.format('%s/frame_%05d.png',out,frame),emu.takeScreenshot()) end
  if frame>=24000 then
    save(out..'/completed.txt','COMPLETED frames=24000; visual inspection and targeted menu tests still required\n')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
