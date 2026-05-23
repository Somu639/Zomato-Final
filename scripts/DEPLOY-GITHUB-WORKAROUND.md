# Deploy when GitHub App auth fails (Railway / Vercel)

GitHub sometimes has incidents with **installation token** auth. Railway/Vercel may show:

- `Bad credentials`
- `repository not authorized`

**This is not a bug in ZM.** Use CLI deploy until GitHub recovers.

## Backend → Railway CLI

```powershell
npm install -g @railway/cli
railway login
cd c:\Users\din17512\Music\ZM
railway init          # or: railway link
railway variables set GROQ_API_KEY=your-key
railway variables set CORS_ORIGINS=https://your-app.vercel.app
railway variables set WEB_HOST=0.0.0.0
railway up
railway domain
```

## Frontend → Vercel CLI

```powershell
npm install -g vercel
cd c:\Users\din17512\Music\ZM\frontend
vercel login
vercel --prod
```

Set `NEXT_PUBLIC_API_BASE_URL` to your Railway URL in the Vercel project settings.

## Full guide

See [Docs/Deployment-Railway-Vercel.md](../Docs/Deployment-Railway-Vercel.md) Part 7.
