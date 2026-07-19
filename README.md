# Alexa's Input (AI) - Podcast Website

Official website for **Alexa's Input (AI)** podcast - technical conversations on AI infrastructure and inference.

## 🎙️ About

A technical podcast where field deployment engineer Alexa Griffith interviews builders and thought leaders about AI inference, infrastructure, and production systems. Going beneath the surface to understand the mechanisms.

## 🌐 Links

- **YouTube:** https://youtube.com/@alexasinput
- **Spotify:** https://open.spotify.com/show/7uBXZa8rP4ZDPXN3eKQw3K
- **Substack:** https://alexasinput.substack.com
- **Website:** alexasinput.ai

## 🎨 Design System

Built with the **Inferra Design System** - a dark-first developer-tool palette featuring:
- Near-black navy surfaces
- Cool neutral text hierarchy
- Indigo brand accent (#5B6CF0)
- Cyan compute accents for AI theming (#1FAFAF)

## 🚀 Deployment

This site is designed to be hosted on **GitHub Pages** with a custom domain (`alexasinput.ai`).

### Setup GitHub Pages

1. Push this repo to GitHub
2. Enable GitHub Pages in repo settings (Settings > Pages)
3. Set source to `main` branch, root directory
4. Configure custom domain `alexasinput.ai`

### Custom Domain Setup

1. In your domain registrar (e.g., Namecheap, Cloudflare), add DNS records:
   ```
   A     @    185.199.108.153
   A     @    185.199.109.153
   A     @    185.199.110.153
   A     @    185.199.111.153
   CNAME www  <your-github-username>.github.io
   ```

2. In GitHub repo settings > Pages:
   - Enter custom domain: `alexasinput.ai`
   - Enable "Enforce HTTPS"

## 📁 Structure

```
alexasinput.ai/
├── index.html       # Main website
├── styles.css       # Inferra-based design system
├── README.md        # This file
└── CNAME            # Custom domain config (add after repo created)
```

## 🔧 Local Development

Simply open `index.html` in a browser, or use a local server:

```bash
python3 -m http.server 8000
# Visit http://localhost:8000
```

## 📊 SEO Optimizations

- Semantic HTML structure
- Meta descriptions and Open Graph tags
- Proper heading hierarchy (H1 → H6)
- Alt text for images (when added)
- Fast loading with minimal CSS/JS
- Mobile responsive design

## 🎯 Future Enhancements

- [ ] Dynamic episode loading from Substack RSS
- [ ] Episode player embeds
- [ ] Search functionality
- [ ] Analytics integration
- [ ] Newsletter signup form
- [ ] Guest photo gallery

## 📝 License

© 2026 Alexa Griffith. All rights reserved.
