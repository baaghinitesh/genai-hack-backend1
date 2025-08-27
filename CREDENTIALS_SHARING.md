# 🔐 Secure Credentials Sharing Guide

## 🚨 IMPORTANT: Never Share Credentials Publicly

This guide shows how to securely share Google Cloud credentials with your team members.

## 📋 What Your Teammates Need

### 1. Google Cloud Service Account Key

Your teammates need the `servicekey.json` file to access Google Cloud services.

### 2. Environment Variable Setup

They need to set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

## 🔒 Secure Sharing Methods

### Method 1: Direct File Transfer (Recommended)

1. **Share the `servicekey.json` file directly** via:

   - Team chat (Discord, Slack, Teams)
   - Email (if secure)
   - File sharing service (Google Drive, Dropbox)
   - USB drive

2. **Instructions for teammates:**
   ```
   Download the servicekey.json file
   Place it in: backned-hck/servicekey.json
   Set environment variable: GOOGLE_APPLICATION_CREDENTIALS=./servicekey.json
   ```

### Method 2: Google Cloud Console Access

1. **Add teammates to your Google Cloud project:**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to IAM & Admin > IAM
   - Click "Add"
   - Add their email addresses
   - Grant "Service Account Key Admin" role

2. **Teammates can then:**
   - Access the Google Cloud Console
   - Go to IAM & Admin > Service Accounts
   - Find: `n8n-550@n8n-local-463912.iam.gserviceaccount.com`
   - Create their own key (JSON format)
   - Download and use locally

### Method 3: Environment Variables (Advanced)

For production environments, use environment variables:

```bash
# Set in your system environment
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/servicekey.json"

# Or use .env file (add to .gitignore)
echo "GOOGLE_APPLICATION_CREDENTIALS=./servicekey.json" > .env
```

## 📝 Quick Setup Instructions for Teammates

### Step 1: Get the Service Key

Ask your team lead for the `servicekey.json` file.

### Step 2: Place the File

```bash
# Place in your project root
cp /path/to/downloaded/servicekey.json backned-hck/servicekey.json
```

### Step 3: Set Environment Variable

```bash
# Windows
set GOOGLE_APPLICATION_CREDENTIALS=D:\calmira\backned-hck\servicekey.json

# macOS/Linux
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/backned-hck/servicekey.json
```

### Step 4: Test Setup

```bash
# Test that credentials work
python -c "from google.cloud import aiplatform; print('✅ Authentication successful!')"
```

## 🚨 Security Checklist

### ✅ DO:

- Share credentials only with trusted team members
- Use secure channels for sharing
- Keep credentials in `.gitignore`
- Rotate credentials if compromised
- Use environment variables in production

### ❌ DON'T:

- Commit credentials to Git
- Share credentials publicly
- Post credentials in public forums
- Use the same credentials for multiple projects
- Leave credentials in plain text files

## 🔄 Credential Rotation

If credentials are compromised:

1. Go to Google Cloud Console
2. Navigate to IAM & Admin > Service Accounts
3. Find your service account
4. Delete the compromised key
5. Create a new key
6. Share new key with team securely
7. Update all team members

## 📞 Emergency Contacts

If you suspect credentials are compromised:

1. **Immediately** revoke the key in Google Cloud Console
2. Create a new key
3. Notify all team members
4. Update all systems using the old key

---

**Remember: Security is everyone's responsibility! 🔒**
