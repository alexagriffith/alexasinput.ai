# Domain Setup Guide for alexasinput.ai

## ✅ GitHub Setup (Complete)

- [x] Repository created: https://github.com/alexagriffith/alexasinput.ai
- [x] GitHub Pages enabled
- [x] CNAME file added for custom domain
- [x] Site deployed to: http://alexasinput.ai

## 🌐 DNS Configuration (Required)

To make `alexasinput.ai` work, you need to configure DNS records with your domain registrar.

### Option 1: Using Vercel (Recommended - Faster & Better Performance)

Vercel offers:
- ✅ Instant global CDN
- ✅ Automatic HTTPS
- ✅ Better performance than GitHub Pages
- ✅ Easy domain setup
- ✅ Free for personal projects

**Vercel Setup:**

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy to Vercel:
   ```bash
   cd /Users/algriffi/github/alexasinput.ai
   vercel --prod
   ```

3. Add custom domain in Vercel dashboard:
   - Go to https://vercel.com/dashboard
   - Select your project
   - Settings > Domains
   - Add `alexasinput.ai`
   - Vercel will provide DNS records to add

### Option 2: Using GitHub Pages

If you prefer GitHub Pages, add these DNS records at your domain registrar:

**A Records (point to GitHub Pages):**
```
Type  Name  Value
A     @     185.199.108.153
A     @     185.199.109.153
A     @     185.199.110.153
A     @     185.199.111.153
```

**CNAME Record (www subdomain):**
```
Type   Name  Value
CNAME  www   alexagriffith.github.io
```

## 🔧 Where to Buy the Domain

Popular registrars:
- **Namecheap** - https://www.namecheap.com
- **Cloudflare** - https://www.cloudflare.com/products/registrar/ (best pricing, $9-10/year)
- **Google Domains** - https://domains.google
- **Porkbun** - https://porkbun.com (affordable, good DNS)

### After Purchasing:

1. Go to your registrar's DNS management
2. Add the A and CNAME records above (if using GitHub Pages)
   - OR follow Vercel's DNS instructions (if using Vercel)
3. Wait 10-60 minutes for DNS propagation
4. Enable HTTPS in GitHub Pages settings (or automatic with Vercel)

## ✅ Verify Setup

Test DNS propagation:
```bash
dig alexasinput.ai
nslookup alexasinput.ai
```

Check HTTPS:
```bash
curl -I https://alexasinput.ai
```

## 📊 Current Status

- **Repository:** https://github.com/alexagriffith/alexasinput.ai
- **GitHub Pages:** Enabled (http://alexasinput.ai - pending DNS)
- **Custom Domain:** Configured in CNAME file
- **HTTPS:** Will be auto-enabled after DNS propagation

## 🎯 Next Steps

1. **Purchase the domain** `alexasinput.ai`
2. **Choose hosting:**
   - **Vercel** (recommended) - Run `vercel --prod`
   - **GitHub Pages** - Configure DNS records above
3. **Wait for DNS propagation** (10-60 minutes)
4. **Enable HTTPS** (automatic with Vercel, manual in GitHub Pages settings)
5. **Test the site** at https://alexasinput.ai

---

**Recommendation:** Use Vercel for better performance, instant HTTPS, and easier management. GitHub Pages works but is slower and requires manual HTTPS setup.
