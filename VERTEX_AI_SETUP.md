# Vertex AI Setup Guide

## Prerequisites
Your Google Cloud project ID is already set in `.env`: `gen-lang-client-0367305329`

## Step 1: Authenticate with Google Cloud

```bash
# Initialize gcloud (if first time)
gcloud init

# Set your project
gcloud config set project gen-lang-client-0367305329

# Authenticate for Application Default Credentials (ADC)
gcloud auth application-default login
```

This will open a browser window for you to log in with your Google account.

## Step 2: Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Generative AI API
gcloud services enable generativelanguage.googleapis.com
```

## Step 3: Verify Setup

```bash
# Check your current project
gcloud config get-value project

# List enabled services
gcloud services list --enabled | grep -E "(aiplatform|generativelanguage)"
```

## Step 4: Test the Agent

```bash
cd /Users/christianmeyndt/PyCharmMiscProject/puckmind
source venv/bin/activate
python src/agent.py
```

## Troubleshooting

### If you get permission errors:
```bash
# Make sure you're logged in
gcloud auth list

# Re-authenticate if needed
gcloud auth application-default login
```

### If Vertex AI quota is also exhausted:
- Vertex AI has much higher quotas than the free API
- Check quota at: https://console.cloud.google.com/iam-admin/quotas
- You may need to enable billing for unlimited access

## Vertex AI Pricing (Pay-as-you-go)
- Gemini 2.0 Flash: Very low cost (~$0.00001 per 1K tokens)
- Much higher free tier than Google AI API
- See: https://cloud.google.com/vertex-ai/generative-ai/pricing
