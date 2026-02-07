# Tailscale VPN Setup for Windows

Connect Railway-hosted Synch-Manager to your local TP4100 (10.0.0.72) using Tailscale VPN.

## ✅ Step 1: Install Tailscale on Windows Laptop

### Download & Install
1. Go to: **https://tailscale.com/download/windows**
2. Download `tailscale-setup-latest.exe`
3. Run the installer
4. Click through the installation wizard
5. Allow Windows Firewall access when prompted

### Sign In
1. Tailscale will auto-launch after installation
2. Click **"Sign In"** button
3. Choose your authentication provider:
   - Google
   - Microsoft
   - GitHub
   - Or create Tailscale account
4. Complete authentication in browser

### Verify Installation
Open **PowerShell** (Windows Key + X → Windows PowerShell):

```powershell
# Check Tailscale status
tailscale status

# Get your Tailscale IP address
tailscale ip -4
```

You'll see output like: `100.64.1.5`

**📝 IMPORTANT: Write down this IP address!**

---

## ✅ Step 2: Verify TP4100 Accessibility

From PowerShell, test if you can reach your TP4100:

```powershell
# Ping TP4100
ping 10.0.0.72

# You should see replies like:
# Reply from 10.0.0.72: bytes=32 time<1ms TTL=64
```

✅ If ping works, your Windows laptop can reach TP4100!

---

## ✅ Step 3: Get Tailscale Auth Key

1. Go to: **https://login.tailscale.com/admin/settings/keys**
2. Click **"Generate auth key"** button
3. Configure the key:
   - ✅ Check **"Reusable"**
   - ✅ Check **"Ephemeral"** (optional)
   - Set **Expiration**: 90 days
4. Click **"Generate key"**
5. **Copy the key** - looks like: `tskey-auth-kABCDEF123456-xyz789abc`

**⚠️ SAVE THIS KEY SECURELY - YOU'LL NEED IT FOR RAILWAY!**

---

## ✅ Step 4: Add Tailscale Auth Key to Railway

1. Go to Railway project: **https://railway.com/project/282ea725-75e6-4970-a77e-cffc243fe851**
2. Click on **"synch-manager"** service (backend)
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add:
   - Name: `TAILSCALE_AUTH_KEY`
   - Value: `tskey-auth-kABCDEF123456-xyz789abc` (your key)
6. Click **"Add"**

---

## ✅ Step 5: Configure Railway Deployment

The Railway backend needs to:
1. Install Tailscale during build
2. Connect to Tailscale network on startup
3. Then start Django

This is already configured in the repository via `Procfile` and `nixpacks.toml`.

---

## ✅ Step 6: Update TP4100 IP in Django Admin

Once Railway connects to Tailscale:

1. Check your Windows laptop's Tailscale IP again:
   ```powershell
   tailscale ip -4
   ```
   Example output: `100.64.1.5`

2. Go to Django admin: **https://synch-manager-production.up.railway.app/admin/inventory/networkelement/2/change/**

3. Update **TP4100-Main** IP address:
   - ❌ Old: `10.0.0.72` (local network - Railway can't reach)
   - ✅ New: `100.64.1.5` (your Tailscale IP - Railway CAN reach!)

4. Click **"Save"**

---

## ✅ Step 7: Set Up Subnet Router (Forward Traffic to 10.0.0.72)

Your Windows laptop needs to forward traffic from Tailscale network to your local 10.0.0.0/24 network:

In **PowerShell (Run as Administrator)**:

```powershell
# Enable subnet routing
tailscale up --advertise-routes=10.0.0.0/24 --accept-routes
```

Then:
1. Go to: **https://login.tailscale.com/admin/machines**
2. Find your Windows machine
3. Click **"..."** (three dots)
4. Click **"Edit route settings..."**
5. ✅ Enable **"Use as subnet router"**
6. ✅ Approve the subnet: `10.0.0.0/24`
7. Click **"Save"**

---

## ✅ Step 8: Test the Connection

### From Django Admin
1. Go to: **https://synch-manager-production.up.railway.app/admin/inventory/networkelement/2/change/**
2. Scroll down and click **"Save"** to trigger a poll

### Check Logs
Go to Railway and check the deployment logs for SNMP polling activity.

### Verify Data
After 1 minute, refresh Django admin and check if SNMP fields are populated:
- Firmware version
- Serial number 
- System description
- Uptime

---

## 🎯 Architecture

```
Railway (Cloud)              Tailscale VPN              Your Network
┌─────────────────┐          ┌─────────────┐          ┌─────────────┐
│                 │          │             │          │             │
│ Synch-Manager   ├─────────►│  100.x.x.x  ├─────────►│ 10.0.0.72   │
│ (Django/Celery) │  SNMP    │  Tailscale  │  Route   │ TP4100      │
│                 │          │  Network    │  Forward │             │
└─────────────────┘          └─────────────┘          └─────────────┘
                              Windows Laptop
                              (Subnet Router)
```

---

## 🔍 Troubleshooting

### Tailscale not connecting?
```powershell
# Check status
tailscale status

# Restart Tailscale
tailscale down
tailscale up
```

### Can't reach 10.0.0.72 from Railway?
1. Verify subnet router is enabled (Step 7)
2. Check Windows Firewall isn't blocking Tailscale
3. Verify `10.0.0.0/24` route is approved in Tailscale admin

### SNMP not working?
```powershell
# Test SNMP from Windows
snmpwalk -v2c -c public 10.0.0.72 system
```

---

## 🚀 Success Indicators

✅ Tailscale icon in Windows system tray shows "Connected"
✅ `tailscale status` shows both Windows and Railway machines
✅ Railway logs show "Tailscale connection established"
✅ Django admin TP4100 fields populate with real data
✅ Dashboard shows real metrics from 10.0.0.72

---

## 📚 Additional Resources

- Tailscale Documentation: https://tailscale.com/kb/
- Subnet Routers: https://tailscale.com/kb/1019/subnets/
- Windows Setup: https://tailscale.com/kb/1022/windows/
