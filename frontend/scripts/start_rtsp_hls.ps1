# 启动FFmpeg将RTSP转换为HLS并输出到前端public目录
# 运行方法：在PowerShell中右键执行或运行命令：
#   powershell -ExecutionPolicy Bypass -File ./scripts/start_rtsp_hls.ps1

$rtsp = "rtsp://admin:okwy1234@172.16.160.43:554/Streaming/Channels/101/H264"
$outDir = "d:\Users\Desktop\new\frontend\public\streams\cam1"
$outFile = Join-Path $outDir "index.m3u8"

# 创建输出目录
if (!(Test-Path -Path $outDir)) {
  New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

# 检查ffmpeg是否可用
$ffmpeg = "ffmpeg"
$ffmpegExists = $false
try {
  $version = & $ffmpeg -version 2>$null
  $ffmpegExists = $true
} catch {
  Write-Host "未找到ffmpeg，请先安装并添加到PATH" -ForegroundColor Red
  exit 1
}

Write-Host "开始转码RTSP到HLS..." -ForegroundColor Green
Write-Host "RTSP: $rtsp" -ForegroundColor Yellow
Write-Host "输出: $outFile" -ForegroundColor Yellow

# 使用低延时HLS设置，删除旧分片，保持短播放列表
# 若RTSP无音频，使用 -an；如果需要重编码可改为 -c:v libx264 -preset veryfast -tune zerolatency
& $ffmpeg -rtsp_transport tcp -i $rtsp -fflags nobuffer -flags low_delay -c:v copy -an -f hls -hls_time 1 -hls_list_size 6 -hls_flags delete_segments+append_list+omit_endlist -y $outFile