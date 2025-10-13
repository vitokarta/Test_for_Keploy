# Keploy DNS 解析問題分析

## 問題描述

在錄製模式下可以成功連接 GitHub API，但在測試模式使用 `--global-passthrough` 時失敗：

```
ERROR   failed to dial the conn to destination server
{"proxy port": 16789, "server address": "[::1]:443", "error": "dial tcp [::1]:443: connect: connection refused"}
```

## 根本原因

### Keploy DNS 攔截機制

Keploy 在**所有模式**下都會啟動自己的 DNS 服務器：

```
INFO    starting UDP DNS server at addr :26789
INFO    starting TCP DNS server at addr :26789
INFO    Keploy has taken control of the DNS resolution mechanism
```

**關鍵行為差異**：

| 模式 | DNS 解析行為 | 目的 |
|------|-------------|------|
| **Record** | `api.github.com` → **真實 IP** → 允許連接 | 記錄真實 API 調用 |
| **Test (默認)** | `api.github.com` → **[::1]** (localhost) → 使用 Mock | 攔截並返回 Mock |
| **Test + `--global-passthrough`** | `api.github.com` → **[::1]** → ❌ 連接失敗 | DNS 仍被攔截，但沒有 Mock 也沒有轉發 |

### 為什麼會解析為 [::1]？

在測試模式下，Keploy 的 DNS 服務器會：

1. **攔截所有 DNS 查詢**（包括 `api.github.com`）
2. **返回 localhost 地址**（IPv6 `[::1]` 或 IPv4 `127.0.0.1`）
3. **期待流量經過 Keploy Proxy**（port 16789）來匹配 Mock

但是，當使用 `--global-passthrough` 時：
- DNS 解析仍返回 `[::1]`
- 應用嘗試連接 `[::1]:443`
- **該地址沒有服務** → 連接失敗

## 為什麼錄製模式能成功？

在錄製模式下，Keploy 的行為不同：

1. **DNS 查詢被攔截**
2. **解析到真實 IP 地址**（或通過 DNS 轉發）
3. **流量經過 Keploy Proxy**
4. **Proxy 建立到真實 API 的連接**
5. **記錄請求和回應**

關鍵差異：**錄製模式允許 DNS 解析到真實 IP**。

## 驗證問題

### 測試 1：檢查 DNS 解析

在錄製時：
```bash
docker compose exec student-backend nslookup api.github.com
# 應返回真實 GitHub IP
```

在測試時：
```bash
docker compose exec student-backend nslookup api.github.com
# 可能返回 localhost 或 Keploy 攔截的地址
```

### 測試 2：查看環境變數

Keploy 會設置 DNS 相關環境變數：
```bash
docker compose exec student-backend env | grep -i dns
```

## 潛在解決方案

### 選項 1：禁用 Keploy DNS（不推薦，可能不支援）

理論上需要告訴 Keploy 不要攔截 DNS，但這可能破壞 Keploy 的核心功能。

### 選項 2：使用主機網路（Host Network）

```yaml
# docker-compose.yml
services:
  student-backend:
    network_mode: "host"
```

**問題**：這會繞過 Keploy 的網路攔截，無法錄製。

### 選項 3：手動配置 DNS 轉發

在 Dockerfile 中添加：
```dockerfile
# 強制使用真實 DNS
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

**問題**：Docker 會覆蓋 resolv.conf，這不會生效。

### 選項 4：使用 IP 地址而不是域名（不實用）

```python
# 直接使用 GitHub API 的 IP
response = await client.get("https://140.82.121.6/users/vitokarta")
```

**問題**：
- GitHub 使用 CDN，IP 會變化
- HTTPS 證書驗證會失敗

### 選項 5：混合模式 - 部分 Mock + 部分真實（推薦）

使用 Keploy 的 Mock 進行測試，但為特定服務啟用 passthrough：

```bash
keploy test ... --pass-through-ports 443
```

**問題**：從你的測試看，這仍然有 DNS 攔截問題。

## 結論

### 核心矛盾

**Keploy 的設計哲學**：
- 測試模式 = 使用 Mock（隔離、快速、可重複）
- 錄製模式 = 連接真實服務（捕獲真實行為）

**你的需求**：
- 測試模式 = 選擇性地連接真實外部服務

這兩者存在**架構層面的衝突**。

### 為什麼 Keploy 這樣設計？

1. **一致性**：確保測試在任何環境都能重現
2. **速度**：避免網路延遲
3. **穩定性**：不依賴外部服務可用性
4. **隔離性**：測試不應影響外部系統

### 當前最佳實踐

**對於你的場景**，建議採用以下策略：

1. **關鍵外部服務**（如 GitHub API）→ 使用 Keploy Mock
2. **內部服務**（如 MySQL）→ 使用真實服務（`--pass-through-ports 3306`）

這樣既能保證測試穩定性，又能測試真實的數據庫互動。

## 深入調查建議

如果你確實需要在測試模式連接真實外部 API，建議：

1. **查看 Keploy GitHub Issues**
   - 搜尋關鍵字：DNS, passthrough, external API, test mode
   - 提交 Feature Request

2. **研究 Keploy 原始碼**
   - 查看 `pkg/core/proxy/tls/` 目錄
   - 查看 DNS 解析邏輯

3. **考慮替代方案**
   - 使用環境變數切換 Mock/真實 API
   - 實作自己的條件式 Mock 層

## 參考資料

- [Keploy DNS 控制機制](https://keploy.io/docs/running-keploy/docker-tls/)
- [Keploy GitHub Issues](https://github.com/keploy/keploy/issues)
