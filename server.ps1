$port = 8080
$url = "http://localhost:$port/"
$root = $PSScriptRoot

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($url)
try {
    $listener.Start()
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " 🌌 GOPIREDDY GOPAL - 3D CINEMATIC PORTFOLIO LOCAL SERVER" -ForegroundColor Green
    Write-Host " Streaming at: $url" -ForegroundColor Yellow
    Write-Host " Press Ctrl+C in this window anytime to stop the server." -ForegroundColor Gray
    Write-Host "==========================================================" -ForegroundColor Cyan
    Start-Process "$url"

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        $relPath = $request.Url.LocalPath.TrimStart('/')
        if ([string]::IsNullOrEmpty($relPath)) { $relPath = "index.html" }
        $filePath = Join-Path $root $relPath

        if (Test-Path $filePath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $mime = switch ($ext) {
                ".html" { "text/html; charset=utf-8" }
                ".css"  { "text/css; charset=utf-8" }
                ".js"   { "application/javascript; charset=utf-8" }
                ".json" { "application/json; charset=utf-8" }
                ".mp4"  { "video/mp4" }
                ".png"  { "image/png" }
                ".jpg"  { "image/jpeg" }
                ".svg"  { "image/svg+xml" }
                ".zip"  { "application/zip" }
                default { "application/octet-stream" }
            }
            $response.ContentType = $mime
            $response.AddHeader("Access-Control-Allow-Origin", "*")
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
            $response.OutputStream.Write($msg, 0, $msg.Length)
        }
        $response.Close()
    }
} catch {
    Write-Host "Server notice: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    if ($listener.IsListening) { $listener.Stop() }
}
