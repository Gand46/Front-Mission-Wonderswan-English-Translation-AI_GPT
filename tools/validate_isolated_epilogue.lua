-- SYNTHETIC_STATE: activate before the first portrait, at frame 4200.
-- The previous 4600-frame probe left a live portrait in both JP and EN ROMs.
-- Disable the previous battle updater via WRAM 0900 bit 0 (gate at 7801F7).
-- No text pointer substitution, no ROM edits, no timer or page-counter changes.
local final=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local out=assert(final:match('^(.*)[/\\]'))
local function save(p,b)local f=assert(io.open(p,'wb'));f:write(b);f:close()end
local trace=assert(io.open(out..'/trace.tsv','w'))
trace:write('frame\tkind\taddress\tvalue\tcs\tip\n')
local frame=0;local stopframe=36000;local activated=false;local counts={};local roots={0,0};local list={};local captures={};local pending={}
local function rd(p)return emu.read(p,emu.memType.wsMemory)end
local function word(p)return rd(p)+256*rd(p+1)end
local function log(kind,address,value)
 local s=emu.getState();trace:write(string.format('%d\t%s\t%X\t%X\t%04X\t%04X\n',frame,kind,address,value,s['cpu.cs'],s['cpu.ip']));trace:flush()
end
local function wrword(p,v)emu.write(p,v%256,emu.memType.wsMemory);emu.write(p+1,math.floor(v/256),emu.memType.wsMemory)end
emu.addMemoryCallback(function(address,value)
 local i=math.floor(((address%65536)-0x27c0)/4)
 if activated then
  counts[i]=(counts[i]or 0)+1
  if ((address%65536)-0x27c0)%4==0 then log('main',address,i);pending[#pending+1]={at=frame+170,index=i}end
 end
end,emu.callbackType.read,0x7427c0,0x745c37,emu.cpuType.ws,emu.memType.wsPrgRom)
emu.addMemoryCallback(function(address,value)
 if activated then log('native_index',address,value);list[value]=(list[value]or 0)+1 end
end,emu.callbackType.read,0x7ec6a8,0x7ec6f5,emu.cpuType.ws,emu.memType.wsPrgRom)
for j,q in ipairs({{0x7cc124,0x7cc133},{0x7cc58c,0x7cc5b1}})do
 emu.addMemoryCallback(function(address,value)roots[j]=roots[j]+1;log('legacy_root_'..j,address,value)end,emu.callbackType.read,q[1],q[2],emu.cpuType.ws,emu.memType.wsPrgRom)
end
emu.addMemoryCallback(function(address,value)if activated then log('native_init',address,value)end end,emu.callbackType.exec,0x7ee5a0,0x7ee5a0,emu.cpuType.ws,emu.memType.wsPrgRom)
local route={{20,24,'start'},{80,84,'start'},{140,144,'start'},{220,224,'start'},{300,304,'a'},{380,384,'start'},{460,464,'a'},{540,544,'start'},{620,624,'a'},{700,704,'a'},{780,784,'start'},{860,864,'a'},{940,944,'a'},{1020,1024,'start'},{1100,1104,'a'}}
emu.addEventCallback(function()
 local t={start=false,a=false,b=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false}
 if not activated then
  for _,p in ipairs(route)do if frame>=p[1]and frame<=p[2]then t[p[3]]=true end end
  if frame>=1220 and frame%20<=2 then t.a=true end
 end
 emu.setInput(t,0)
end,emu.eventType.inputPolled)
local last=''
emu.addEventCallback(function()
 frame=frame+1
 if frame==4200 then
  local p=0x19a5+word(0x19a3)
  log('portrait_flag',0x1c53,rd(0x1c53));log('dialog_flag',0x1c52,rd(0x1c52));log('battle_flag',0x900,rd(0x900));log('event_before_activation',p,word(p));activated=true;emu.write(0x900,rd(0x900)&0xfe,emu.memType.wsMemory);log('WRAM_CLEAR_BATTLE_UPDATE_BIT',0x900,rd(0x900));wrword(p,0x58);log('WRAM_WRITE_EVENT_58',p,0x58)
  local api={};for k,v in pairs(emu)do api[#api+1]=k..' '..type(v)end;table.sort(api);save(out..'/api.txt',table.concat(api,'\n'))
 end
 if activated then
  local state=string.format('%02X:%02X:%02X/%04X/%04X/%04X',rd(0x200),rd(0x201),rd(0x202),word(0xeec2),word(0xef42),word(0xef34))
  if state~=last then trace:write(frame..'\tstate\t'..state..'\n');trace:flush();last=state end
  for _,q in ipairs(pending)do if q.at==frame then local name=string.format('text_%04d_frame_%05d.png',q.index,frame);save(out..'/'..name,emu.takeScreenshot());captures[#captures+1]=name end end
  if frame%300==0 then save(string.format('%s/frame_%05d.png',out,frame),emu.takeScreenshot())end
 end
 if frame==stopframe then
  local function obj(t)local a={};for k,v in pairs(t)do a[#a+1]=string.format('"%d":%d',k,v)end;return '{'..table.concat(a,',')..'}'end
  local data='{"classification":"SYNTHETIC_STATE","frames":'..frame..',"activation_frame":4200,"activation_event":88,"rom_modified":false,"text_pointer_injection":false,"main_reads":'..obj(counts)..',"native_index_reads":'..obj(list)..',"legacy_root_reads":['..roots[1]..','..roots[2]..']}'
  save(final,emu.takeScreenshot());save(report,data);trace:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
