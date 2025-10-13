# Keploy 原始碼分析：Test Mode 能否連接真實外部 API

## 核心發現

**結論：Test mode 可以連接真實外部 API，但需要正確配置 `bypassRules` 或使用 `--global-passthrough` flag。**

問題在於 DNS 解析機制的差異，而不是程式碼本身的限制。

---

## 1. DNS 解析機制差異

### Record Mode (dns.go:104-108)
```go
if !found {
    // If not found in cache, resolve the DNS query only in case of record mode
    //TODO: Add support for passThrough here using the src<->dst mapping
    if models.GetMode() == models.MODE_RECORD {
        answers = resolveDNSQuery(p.logger, question.Name)
    }
}
```

**行為**：
- 調用 `resolveDNSQuery()` 使用系統 DNS resolver 獲取真實 IP
- `api.github.com` → 正確的 GitHub IP (例如 140.82.121.6)
- 請求被正常轉發到真實外部服務

### Test Mode (dns.go:110-125)
```go
if len(answers) == 0 {
    switch question.Qtype {
    case dns.TypeA:
        answers = []dns.RR{&dns.A{
            Hdr: dns.RR_Header{Name: question.Name, Rrtype: dns.TypeA, Class: dns.ClassINET, Ttl: 3600},
            A:   net.ParseIP(p.IP4),  // 返回 127.0.0.1
        }}
    case dns.TypeAAAA:
        answers = []dns.RR{&dns.AAAA{
            Hdr:  dns.RR_Header{Name: question.Name, Rrtype: dns.TypeAAAA, Class: dns.ClassINET, Ttl: 3600},
            AAAA: net.ParseIP(p.IP6), // 返回 ::1
        }}
    }
}
```

**行為**：
- **不調用** `resolveDNSQuery()`，直接返回 localhost IP
- `api.github.com` → `::1` (IPv6 localhost) 或 `127.0.0.1`
- 應用程式連接到 localhost:443，但該 port 沒有服務 → **Connection refused**

**這就是你遇到的錯誤原因**：
```
dial tcp [::1]:443: connect: connection refused
```

---

## 2. BypassRules 機制（解決方案一）

### 配置結構 (config/config.go:111-115)
```go
type BypassRule struct {
    Path string `json:"path" yaml:"path" mapstructure:"path"`
    Host string `json:"host" yaml:"host" mapstructure:"host"`
    Port uint   `json:"port" yaml:"port" mapstructure:"port"`
}
```

### 實作邏輯 (utils/utils.go:163-199)
```go
func IsPassThrough(logger *zap.Logger, req *http.Request, destPort uint, opts models.OutgoingOptions) bool {
    passThrough := false

    for _, bypass := range opts.Rules {
        // 1. Host 匹配（支援 regex）
        if bypass.Host != "" {
            regex, err := regexp.Compile(bypass.Host)
            if err != nil {
                continue
            }
            passThrough = regex.MatchString(req.Host)
            if !passThrough {
                continue
            }
        }

        // 2. Path 匹配（支援 regex）
        if bypass.Path != "" {
            regex, err := regexp.Compile(bypass.Path)
            if err != nil {
                continue
            }
            passThrough = regex.MatchString(req.URL.String())
            if !passThrough {
                continue
            }
        }

        // 3. Port 匹配（可選）
        if passThrough {
            if bypass.Port == 0 || bypass.Port == destPort {
                return true
            }
            passThrough = false
        }
    }

    return passThrough
}
```

### 使用範例
在 `keploy.yml` 中配置：

```yaml
bypassRules:
  - host: "api.github.com"        # 精確匹配
  - host: ".*\\.github\\.com"     # Regex 匹配所有 GitHub 子域名
  - host: "api\\..*\\.com"        # 匹配所有 api.*.com
    port: 443                      # 只針對 HTTPS
```

**重要發現**：
- ✅ `bypassRules` 已在程式碼中實作
- ✅ 支援 regex 匹配，非常靈活
- ✅ 可針對特定 Host、Path、Port 進行 bypass
- ❌ **但 DNS 層面沒有對應的 bypass 邏輯**（dns.go:105 有 TODO 註解）

---

## 3. Global Passthrough（解決方案二）

### 配置選項 (config/config.go:76)
```go
type Record struct {
    // ...
    GlobalPassthrough bool `json:"globalPassthrough" yaml:"globalPassthrough" mapstructure:"globalPassthrough"`
}
```

### Proxy 初始化 (proxy/proxy.go:83)
```go
func New(logger *zap.Logger, info core.DestInfo, opts *config.Config) *Proxy {
    return &Proxy{
        // ...
        GlobalPassthrough: opts.Record.GlobalPassthrough,  // 從 config 讀取
    }
}
```

### 執行邏輯 (proxy/proxy.go:385-399)
```go
//check for global passthrough in test mode
if p.GlobalPassthrough || (!rule.Mocking && (rule.Mode == models.MODE_TEST)) {
    dstConn, err = net.Dial("tcp", dstAddr)  // 直接連接真實地址
    if err != nil {
        utils.LogError(p.logger, err, "failed to dial the conn to destination server")
        return err
    }

    err = p.globalPassThrough(parserCtx, srcConn, dstConn)  // 透傳所有流量
    if err != nil {
        utils.LogError(p.logger, err, "failed to handle the global pass through")
        return err
    }
    return nil
}
```

### 透傳實作 (proxy/util.go:29-79)
```go
func (p *Proxy) globalPassThrough(ctx context.Context, client, dest net.Conn) error {
    // ...
    for {
        select {
        case buffer := <-clientBuffChan:
            // 直接轉發 client → dest
            _, err := dest.Write(buffer)
        case buffer := <-destBuffChan:
            // 直接轉發 dest → client
            _, err := client.Write(buffer)
        }
    }
}
```

**問題**：
- ⚠️ `GlobalPassthrough` 在 proxy 層有效，但**DNS 層仍然返回 localhost**
- 在 proxy.go:387，code 嘗試 `net.Dial("tcp", dstAddr)`
- 但 `dstAddr` 已經是 `[::1]:443`（因為 DNS 早已解析錯誤）
- **這就是為什麼你使用 `--global-passthrough` 仍然失敗**

---

## 4. 問題根源：DNS 與 Proxy 的分離

### 流程圖

```
Record Mode:
App → DNS Query → Keploy DNS Server → resolveDNSQuery() → 真實 IP
                                                               ↓
App → HTTP Request → eBPF 攔截 → Proxy → 真實外部服務
                                    ↓
                              Record Mock

Test Mode (預期):
App → DNS Query → Keploy DNS Server → localhost IP (::1)
                                           ↓
App → HTTP Request → eBPF 攔截 → Proxy → Mock Manager → 返回 Mock
                                    ✓

Test Mode (使用 --global-passthrough，實際失敗):
App → DNS Query → Keploy DNS Server → localhost IP (::1)  ← 問題在這
                                           ↓
App → HTTP Request to [::1]:443 → eBPF 攔截 → Proxy
                                                 ↓
                                    GlobalPassthrough 檢查 = true
                                                 ↓
                                    net.Dial("tcp", "[::1]:443")  ← 連接失敗！
                                                 ✗
```

### 關鍵程式碼證據

**dns.go:105** - TODO 註解說明了一切：
```go
//TODO: Add support for passThrough here using the src<->dst mapping
```

**這表示開發者知道需要在 DNS 層支援 passthrough，但目前尚未實作。**

---

## 5. 為何 Record Mode 成功但 Test Mode 失敗

| 階段 | Record Mode | Test Mode (default) | Test Mode (--global-passthrough) |
|------|-------------|---------------------|----------------------------------|
| DNS 解析 | ✅ 返回真實 IP | ❌ 返回 localhost | ❌ 返回 localhost |
| Proxy 連接 | ✅ 連接真實服務 | ✅ 連接 Mock | ❌ 嘗試連接 localhost:443 |
| 結果 | ✅ 成功記錄 | ✅ 返回 Mock | ❌ Connection refused |

---

## 6. 解決方案與建議

### ❌ 方案一：使用 `bypassRules`（不可行）
```yaml
bypassRules:
  - host: "api.github.com"
```

**原因**：`bypassRules` 只在 HTTP 請求層生效（utils.go:163），DNS 層沒有對應邏輯。

### ❌ 方案二：使用 `--global-passthrough`（不可行）
```bash
keploy test --global-passthrough
```

**原因**：Proxy 收到的 `dstAddr` 已經是 `[::1]:443`，無法連接真實服務。

### ✅ 方案三：修改 Keploy 原始碼（可行但複雜）

需要修改 `pkg/core/proxy/dns.go`，在 Test Mode 下對 bypass 的 host 調用真實 DNS：

```go
func (p *Proxy) ServeDNS(w dns.ResponseWriter, r *dns.Msg) {
    // ...
    if !found {
        // 新增：檢查是否在 bypassRules 中
        shouldBypass := false
        for _, bypass := range p.config.BypassRules {
            if bypass.Host != "" {
                regex, _ := regexp.Compile(bypass.Host)
                if regex.MatchString(question.Name) {
                    shouldBypass = true
                    break
                }
            }
        }

        // 修改：bypass 的域名在 test mode 也進行真實解析
        if models.GetMode() == models.MODE_RECORD || shouldBypass {
            answers = resolveDNSQuery(p.logger, question.Name)
        }
    }
    // ...
}
```

### 🎯 方案四：僅測試 Mock 功能（目前最實際）

接受 Keploy 的設計限制：
- **Record Mode**：連接真實外部服務並記錄
- **Test Mode**：只使用 Mock，不連接真實服務

這是 Keploy 預期的使用方式，也是大多數 API 測試工具的標準行為。

---

## 7. 架構限制總結

### Keploy 目前的設計假設

1. **Test Mode = 完全隔離測試**
   - 所有外部依賴都應該被 mock
   - DNS 故意返回 localhost 以確保流量被攔截

2. **Record Mode = 正常連接外部**
   - DNS 正常解析
   - 記錄所有真實互動

### 為何不支援「選擇性 Mock」

這是架構層面的設計決策：
- eBPF hook 在 DNS 解析**之前**攔截
- 一旦進入 Test Mode，DNS 就返回 localhost
- Proxy 層的 `GlobalPassthrough` 已經太晚（地址已錯誤）

### TODO 註解的意義

dns.go:105 的 TODO 表示：
- ✅ 開發者**意識到**這個限制
- ✅ 技術上**可以**實作 DNS 層 passthrough
- ❌ 目前**尚未**優先實作
- ❓ 可能認為「Test Mode 不應連接真實服務」是合理設計

---

## 8. 實際建議

對於你的使用情境：

1. **如果目標是測試 Keploy 錄製外部 API 的能力**
   - ✅ Record Mode 已經成功
   - ✅ Test Mode 使用 Mock 也成功
   - ✅ Keploy 功能正常運作

2. **如果需要在 Test 時連接真實外部 API**
   - ❌ 目前 Keploy 不支援此場景
   - 💡 考慮貢獻 PR 實作 DNS 層 bypass（修改 dns.go）
   - 💡 或使用其他測試策略（例如分離 unit test 與 integration test）

3. **如果需要選擇性 Mock**
   - 建議使用專門的 Mock 工具（如 WireMock、Mockoon）
   - 或修改測試架構，將外部 API 調用抽象為可替換的 interface
