local capture_path = assert(os.getenv("MESEN_CAPTURE_PATH"),
	"MESEN_CAPTURE_PATH is not set")
local report_path = assert(os.getenv("MESEN_LUA_REPORT"),
	"MESEN_LUA_REPORT is not set")
local capture_frame = tonumber(os.getenv("MESEN_CAPTURE_FRAME") or "180")
local frames = 0

assert(capture_frame ~= nil and capture_frame > 0,
	"MESEN_CAPTURE_FRAME must be a positive integer")

local function write_file(path, data, mode)
	local file, error_message = io.open(path, mode or "w")
	if file == nil then
		error("cannot write " .. path .. ": " .. tostring(error_message))
	end
	file:write(data)
	file:close()
end

emu.addEventCallback(function()
	frames = frames + 1
	if frames == capture_frame then
		write_file(capture_path, emu.takeScreenshot(), "wb")
		write_file(report_path, string.format([[
{
  "schema": 1,
  "test": "generic Mesen framebuffer preview",
  "passed": true,
  "lua_frames": %d
}
]], frames))
		emu.log("MESEN_PREVIEW_PASS: screenshot captured at frame " .. frames)
		emu.stop(0)
	end
end, emu.eventType.endFrame)

