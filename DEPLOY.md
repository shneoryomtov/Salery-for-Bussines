# Deploy to Vercel Guide

## One-Click Deployment 🚀

Your app is ready to deploy to Vercel! Here are the easiest ways:

### Option 1: Direct Import (Fastest ⭐)

1. Go to https://vercel.com/new
2. Click **Import Git Repository**
3. Paste: `https://github.com/shneoryomtov/Salery-for-Bussines.git`
4. Click **Import**
5. Click **Deploy**

Done! Your app is live in ~30 seconds.

### Option 2: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel auth

# Deploy
cd path/to/Salary-for-Business
vercel
```

### Option 3: GitHub Automatic Deploys

After first deploy on Vercel, any push to `main` branch auto-deploys:

```bash
git push origin main  # Auto-deploys to Vercel! 🎉
```

## First-Time Setup

```bash
# 1. Install dependencies
npm install

# 2. Test locally
npm run dev
# Open http://localhost:3000

# 3. Build for production
npm run build

# 4. Deploy to Vercel
vercel
```

## Environment Variables (Optional)

Currently, the app has **no external dependencies**, but if you add any later:

1. In Vercel dashboard
2. Go to Settings → Environment Variables
3. Add your variables
4. Re-deploy

## Your Live App URL

After deployment to Vercel, your app will have a URL like:
```
https://salary-calculator-israel.vercel.app
```

If you have a custom domain, you can link it in Vercel Dashboard.

## Deployment Status

- ✅ App: Ready for Vercel
- ✅ Source Code: Pushed to GitHub
- ✅ Next.js: v15 (Vercel native)
- ✅ Build Time: ~2 minutes
- ⏳ Deploy Status: Waiting for you!

## Next Steps

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Click **Deploy**
4. Share your live URL with anyone!

---

The app will work exactly like your local version, but **live on the internet** 🌍

Need help? Check Vercel docs: https://vercel.com/docs
