# PuckMind - Google Cloud Deployment Guide

## Option 1: Deploy via Google Cloud Console (Recommended - No Docker needed)

### Step 1: Prepare Code
Your code is ready! All necessary files are in place:
- `Dockerfile` ✅
- `.dockerignore` ✅
- `.gcloudignore` ✅

### Step 2: Deploy via Cloud Console

1. **Open Cloud Console**
   - Go to https://console.cloud.google.com/
   - Select project: `gen-lang-client-0367305329`

2. **Navigate to Cloud Run**
   - Search for "Cloud Run" in the top search bar
   - Click "Cloud Run" service

3. **Create Service**
   - Click "CREATE SERVICE"
   - Choose "Continuously deploy from a repository (source or function)"
   - Click "SET UP WITH CLOUD BUILD"

4. **Connect Repository**
   - Select "GitHub" as source
   - Authenticate with GitHub if needed
   - Select repository: `christian-meyndt/puckmind`
   - Select branch: `main`
   - Build type: `Dockerfile`
   - Dockerfile path: `/Dockerfile`
   - Click "SAVE"

5. **Configure Service**
   - Service name: `puckmind`
   - Region: `us-central1`
   - Authentication: **Allow unauthenticated invocations**
   - Container settings:
     - Memory: `2 GiB`
     - CPU: `1`
     - Request timeout: `300`
     - Maximum instances: `10`

6. **Set Environment Variables**
   Click "VARIABLES & SECRETS" → "ADD VARIABLE":
   
   ```
   MONGODB_URI = mongodb+srv://puckmind_user:rOXufXk4ro21GdEz@cluster0.0eufdiq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   
   GOOGLE_CLOUD_PROJECT = gen-lang-client-0367305329
   
   GOOGLE_CLOUD_LOCATION = us-central1
   
   GOOGLE_GENAI_USE_VERTEXAI = true
   ```

7. **Create Service**
   - Click "CREATE"
   - Wait 3-5 minutes for build and deployment
   - You'll get a URL like: `https://puckmind-[hash]-uc.a.run.app`

---

## Option 2: Deploy with Docker (Requires Docker Desktop)

### Prerequisites
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop

### Deploy Commands
```bash
# Export MongoDB URI
export MONGODB_URI="mongodb+srv://puckmind_user:rOXufXk4ro21GdEz@cluster0.0eufdiq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Run deployment script
./deploy-local.sh
```

---

## Option 3: Deploy from Google Cloud Shell

1. **Open Cloud Shell**
   - Go to https://console.cloud.google.com/
   - Click the Cloud Shell icon (>_) in top right

2. **Clone Repository**
   ```bash
   git clone https://github.com/christian-meyndt/puckmind.git
   cd puckmind
   ```

3. **Set Environment Variables**
   ```bash
   export MONGODB_URI="mongodb+srv://puckmind_user:rOXufXk4ro21GdEz@cluster0.0eufdiq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
   export PROJECT_ID="gen-lang-client-0367305329"
   export REGION="us-central1"
   ```

4. **Build and Deploy**
   ```bash
   gcloud builds submit --tag gcr.io/${PROJECT_ID}/puckmind
   
   gcloud run deploy puckmind \
     --image gcr.io/${PROJECT_ID}/puckmind \
     --platform managed \
     --region ${REGION} \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 1 \
     --timeout 300 \
     --set-env-vars MONGODB_URI=${MONGODB_URI} \
     --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \
     --set-env-vars GOOGLE_CLOUD_LOCATION=${REGION}
   ```

5. **Get URL**
   ```bash
   gcloud run services describe puckmind --region ${REGION} --format 'value(status.url)'
   ```

---

## Troubleshooting

### Permission Denied Errors
- Use **Option 1** (Cloud Console) - it has built-in permissions
- Or use **Option 3** (Cloud Shell) - authenticated automatically

### Build Failures
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check Cloud Build logs in Console

### Runtime Errors
- Verify environment variables are set correctly
- Check Cloud Run logs for errors
- Ensure MongoDB Atlas allows connections from 0.0.0.0/0

---

## Post-Deployment

### Test Your Deployment
1. Visit your Cloud Run URL
2. Try the chat: "Show me top scorers"
3. Test Game Wizard: Add a test game
4. Check schedule page

### Update Deployment
Any git push to `main` branch will trigger auto-redeploy (if using Option 1)

### Get Deployment URL
```bash
gcloud run services describe puckmind \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## For Hackathon Submission

**Your Deployed URL:**
```
https://puckmind-[hash]-uc.a.run.app
```

**Key Points for Devpost:**
- ✅ Deployed on Google Cloud Run
- ✅ Using Vertex AI (Gemini 2.5 Flash)
- ✅ Connected to MongoDB Atlas
- ✅ Serverless, auto-scaling architecture
- ✅ Public URL for judges to test
