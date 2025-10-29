# IP 与端口使用注意事项

本文档说明项目中各处 IP/端口的使用和修改方式，以及常见网络问题的排查与建议。请在不同运行环境（本机、局域网、生产）下参考对应配置。

## 总览
- 后端 Socket 服务（uvicorn）：默认在 `127.0.0.1:5001` 启动，仅本机可访问。
- 前端默认连接地址：`VITE_SOCKET_BASE` 未设置时使用 `http://localhost:5001`。
- 摄像机 IP 示例：`172.16.160.43`（需替换为实际设备地址）。
- 视频流地址示例：`/streams/cam1/index.m3u8`（相对路径，默认同源）。

## 后端 Socket 服务（uvicorn）
- 启动逻辑位置：`backend/ops/apps.py` 的 `OpsConfig.ready()`。
  - 在模型加载成功、且 Django 以 `runserver` 主进程启动时，自动拉起 uvicorn。
  - 若 `127.0.0.1:5001` 已被占用则跳过启动。
- 修改绑定地址/端口：
  - 文件：`backend/ops/apps.py`
  - 关键参数：
    ```python
    host, port = '127.0.0.1', 5001
    cmd = [sys.executable, '-m', 'uvicorn', 'backend.ops.rtsp_socket_server:app',
           '--host', host, '--port', str(port), '--reload']
    ```
  - 局域网访问：将 `host` 改为 `0.0.0.0` 或本机实际 LAN IP（如 `172.16.160.100`）。
  - 生产环境：移除 `--reload` 参数，避免热重载造成重复进程与性能损耗。

### Windows 防火墙
- 若需让其他机器访问，请在 Windows 防火墙中为端口 `5001` 添加入站规则。
- 常见做法：控制面板 → Windows Defender 防火墙 → 高级设置 → 入站规则 → 新建规则。

## 前端连接配置
- 配置项：`VITE_SOCKET_BASE`（如果未设置，默认 `http://localhost:5001`）。
- 设置方法：在 `frontend` 目录创建 `.env.local`（或 `.env`）文件：
  ```env
  VITE_SOCKET_BASE=http://<你的主机或IP>:5001
  ```
- 注意：
  - 若前端与后端不在同一机器，`localhost` 会指向浏览器所在机器，需改为后端的实际 IP。
  - 端口与协议必须与后端一致（如 `http://172.16.160.100:5001`）。

## 摄像机 IP 与视频流
- 示例默认值在 `frontend/src/views/RobotManagement.vue`：
  - 摄像机 IP：`ipAddress = '172.16.160.43'`（示例值，需要替换）。
  - HLS 流地址：`streamUrl = '/streams/cam1/index.m3u8'`。
- 建议：
  - 保证摄像机与后端位于同一网段或可路由互通。
  - 若使用外部流媒体服务器（如 MediaMTX/Nginx），请使用完整 URL（示例：`http://172.16.160.100:8888/streams/cam1/index.m3u8`）。
  - 视频流跨域时需服务端允许跨域或通过反向代理同源化。

## 同机 / 异机运行的选择
- 同机开发：`127.0.0.1` 或 `localhost` 最简单，但仅本机可访问。
- 局域网共享：将后端绑定到真实 LAN IP 或 `0.0.0.0`，前端使用该 IP；开放防火墙端口。
- 生产部署：建议反向代理（Nginx/IIS）统一入口、启用 TLS、限制外网访问范围。

## 多网卡与虚拟网卡
- 使用 `ipconfig` 查看本机的有效 IPv4 地址，避免选择虚拟网卡（如 vEthernet、VPN 的地址）。
- 绑定 `host` 时明确选择要对外服务的网卡对应 IP。

## 常见问题排查
- 端口占用：
  - PowerShell：`Get-NetTCPConnection -LocalPort 5001`
  - 或：`netstat -ano | findstr :5001`
  - 发现占用后，结束对应进程或修改端口。
- 防火墙拦截：
  - 无法从其他机器访问时，检查 Windows 防火墙入站规则。
- 跨域（CORS）：
  - 若前端域名与后端不同源，后端需开启跨域或通过反向代理消除跨域。

## 生产环境建议
- 移除 `--reload` 并开启进程守护（如 NSSM/服务方式）。
- 使用反向代理统一入口，开启 HTTPS。
- 仅绑定内网地址，外网访问通过网关或 VPN 控制。

## 快速修改清单
- 修改后端绑定：`backend/ops/apps.py` 中的 `host`/`port`。
- 设置前端连接：`frontend/.env.local` 中的 `VITE_SOCKET_BASE`。
- 摄像机 IP：在前端页面或后台配置中改为实际设备地址。
- 防火墙：开放入站端口或仅限白名单。