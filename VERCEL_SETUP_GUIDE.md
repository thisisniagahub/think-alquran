# Vercel Environment Variables Setup Guide

## Quick Fix - Add Environment Variables to Vercel

### Step 1: Install Vercel CLI (if not installed)
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Link Project
```bash
cd L:\THINK-QURAN\think-alquran
vercel link
```

### Step 4: Add Environment Variables

#### Option A: Via Vercel CLI
```bash
# Add MongoDB URL (replace with your actual MongoDB connection string)
vercel env add MONGO_URL

# Add Database Name
vercel env add DB_NAME

# Add JWT Secret Key
vercel env add JWT_SECRET_KEY
```

When prompted, enter the values for each environment variable.

#### Option B: Via Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your project: `think-alquran`
3. Navigate to: **Settings** → **Environment Variables**
4. Click **Add New**
5. Add each variable:

**MONGO_URL:**
- Name: `MONGO_URL`
- Value: Your MongoDB connection string
  - For MongoDB Atlas: `mongodb+srv://<user>:<pass>@cluster.mongodb.net/think_alquran_db?retryWrites=true&w=majority`
  - For local dev: `mongodb://localhost:27017`
- Environment: Production, Preview, Development (select all)

**DB_NAME:**
- Name: `DB_NAME`
- Value: `think_alquran_db`
- Environment: Production, Preview, Development (select all)

**JWT_SECRET_KEY:**
- Name: `JWT_SECRET_KEY`
- Value: Generate a secure random string (at least 32 characters)
  - You can generate one at: https://randomkeygen.com/
  - Or use command line to generate a random string
- Environment: Production, Preview, Development (select all)

### Step 5: Redeploy
After adding environment variables, trigger a new deployment:
```bash
vercel --prod
```

Or push a commit to trigger automatic deployment:
```bash
git commit --allow-empty -m "Trigger redeployment"
git push origin main
```

## MongoDB Atlas Setup (Recommended for Production)

### 1. Create Free MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for a free account
3. Create a new cluster (free tier available)

### 2. Get Connection String
1. In MongoDB Atlas dashboard, click **Connect**
2. Choose **Connect your application**
3. Copy the connection string
4. Replace `<password>` with your database password
5. Replace `<dbname>` with `think_alquran_db`

Example format:
```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/think_alquran_db?retryWrites=true&w=majority
```

### 3. Whitelist Vercel IPs
In MongoDB Atlas:
1. Go to **Network Access**
2. Click **Add IP Address**
3. Select **Allow Access from Anywhere** (0.0.0.0/0)
   - Or add specific Vercel IPs for better security

## Troubleshooting

### Error: "Secret 'mongo_url' does not exist"
- Make sure environment variable names match exactly (case-sensitive)
- Vercel expects environment variables, not secrets
- Remove `@` prefix from vercel.json if not using secrets

### Error: "Cannot connect to MongoDB"
- Verify MongoDB connection string is correct
- Check if MongoDB Atlas cluster is running
- Verify network access settings allow Vercel IPs

### Deployment Still Failing
1. Check Vercel deployment logs
2. Verify all environment variables are added
3. Try redeploying after adding variables
4. Check that vercel.json references match environment variable names

## Alternative: Simplify vercel.json

If you prefer not to use secrets, update vercel.json:

```json
{
  "env": {
    "MONGO_URL": "MONGO_URL",
    "DB_NAME": "DB_NAME",
    "JWT_SECRET_KEY": "JWT_SECRET_KEY"
  }
}
```

Then add these as regular environment variables (not secrets) in Vercel dashboard.
