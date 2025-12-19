# 🚀 AI Mock Interview Platform - Setup Guide

Complete setup instructions to get your AI Mock Interview Platform running locally.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **npm** or **bun** (package manager)
- **Git** (for cloning the repository)

## 🛠️ Step-by-Step Setup

### 1️⃣ Clone the Repository

```bash
git clone <your-repository-url>
cd Mock\ Interview
```

---

## 🔧 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd ai-mock-interview-backend
```

### Step 2: Create Python Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create your `.env` file from the example:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### Step 5: Edit `.env` File

Open `ai-mock-interview-backend/.env` and fill in the required values:

```env
# VAPI Configuration - Get from https://vapi.ai/dashboard
VAPI_API_KEY=your_actual_vapi_private_key_here
VAPI_WEBHOOK_SECRET=your_webhook_secret_from_vapi_dashboard

# OpenAI (if needed for additional features)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
SECRET_KEY=generate_a_random_secret_key_here
```

**💡 Tips:**
- Get VAPI keys from [VAPI Dashboard](https://vapi.ai/dashboard)
- Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Other settings can remain as default for local development

### Step 6: Initialize Database

```bash
# The database will be created automatically on first run
# For SQLite (default): interview_platform.db will be created
```

### Step 7: Start Backend Server

```bash
# Make sure you're in ai-mock-interview-backend directory
uvicorn app.main:app --reload
```

Backend should now be running at: **http://localhost:8000**

Test it: Open http://localhost:8000/docs to see the API documentation.

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend Directory

Open a **new terminal** and navigate to frontend:

```bash
cd ai-mock-interview-frontend
```

### Step 2: Install Dependencies

**Using npm:**
```bash
npm install
```

**Using bun (faster):**
```bash
bun install
```

### Step 3: Configure Environment Variables

Create your `.env.local` file from the example:

```bash
# Windows
copy .env.example .env.local

# macOS/Linux
cp .env.example .env.local
```

### Step 4: Edit `.env.local` File

Open `ai-mock-interview-frontend/.env.local` and fill in your VAPI credentials:

```env
# VAPI Configuration - Get from https://vapi.ai/dashboard
NEXT_PUBLIC_VAPI_PUBLIC_KEY=pk_your_actual_public_key_here
NEXT_PUBLIC_VAPI_ASSISTANT_ID=asst_your_assistant_id_here

# API Configuration (should match backend URL)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**💡 Tips:**
- Use VAPI **Public Key** (starts with `pk_`) for frontend
- Get Assistant ID from your VAPI dashboard after creating an assistant
- Ensure NEXT_PUBLIC_API_URL matches your backend URL

### Step 5: Start Frontend Development Server

```bash
# Using npm
npm run dev

# Using bun
bun dev
```

Frontend should now be running at: **http://localhost:3000**

---

## 🔑 Getting VAPI Credentials

### 1. Create VAPI Account
- Go to [https://vapi.ai](https://vapi.ai)
- Sign up for an account

### 2. Get API Keys
- Navigate to Dashboard → Settings → API Keys
- Copy your **Private API Key** (for backend .env)
- Copy your **Public API Key** (for frontend .env.local)

### 3. Create Voice Assistant
- Go to Dashboard → Assistants → Create New
- Configure your assistant with interview prompts
- Copy the **Assistant ID** (for frontend .env.local)

### 4. Set Webhook (Optional)
- In Assistant settings, add webhook URL: `http://localhost:8000/api/vapi/webhook`
- Generate and save the webhook secret (for backend .env)

---

## Verification Steps

### Backend Verification

1. **Check API Docs:**
   - Visit: http://localhost:8000/docs
   - You should see the FastAPI Swagger documentation

2. **Test Health Endpoint:**
   - Visit: http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

3. **Check Database:**
   - File `interview_platform.db` should exist in backend directory

### Frontend Verification

1. **Check Homepage:**
   - Visit: http://localhost:3000
   - Homepage should load without errors

2. **Check Interview Page:**
   - Visit: http://localhost:3000/interview
   - VAPI call button should be visible

3. **Browser Console:**
   - Open Developer Tools (F12)
   - Should see no major errors

---

## 📁 Project Structure

```
Mock Interview/
├── ai-mock-interview-backend/     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py               # Main API routes
│   │   ├── vapi_service.py       # VAPI integration
│   │   ├── ml_service.py         # ML/AI features
│   │   └── models.py             # Database models
│   ├── .env.example              # Environment template
│   ├── .env                      # Your actual config (gitignored)
│   └── requirements.txt          # Python dependencies
│
└── ai-mock-interview-frontend/   # Next.js Frontend
    ├── src/
    │   ├── app/                  # Next.js app directory
    │   ├── components/           # React components
    │   └── hooks/                # Custom React hooks
    ├── .env.example              # Environment template
    ├── .env.local                # Your actual config (gitignored)
    └── package.json              # Node dependencies
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: `ModuleNotFoundError`**
```bash
# Solution: Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Then reinstall dependencies
pip install -r requirements.txt
```

**Issue: `Port 8000 already in use`**
```bash
# Solution: Kill existing process or use different port
uvicorn app.main:app --reload --port 8001
```

**Issue: Database errors**
```bash
# Solution: Delete and recreate database
rm interview_platform.db
# Restart server - database will be recreated
```

### Frontend Issues

**Issue: `Module not found`**
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules .next
npm install  # or bun install
```

**Issue: VAPI not connecting**
- Check that VAPI keys are correct in `.env.local`
- Ensure keys start with correct prefix (`pk_` for public key)
- Verify Assistant ID is correct
- Check browser console for specific error messages

**Issue: `Cannot connect to backend`**
```bash
# Solution: Verify backend is running
# Check NEXT_PUBLIC_API_URL in .env.local matches backend URL
```

---

## 🔒 Security Notes

⚠️ **Important:**
- Never commit `.env` or `.env.local` files to git
- Keep your API keys secret
- Use environment variables for all sensitive data
- For production, use proper secret management

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [VAPI Documentation](https://docs.vapi.ai/)
- [Project README](./README.md)

---

## 🆘 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Review terminal error messages
3. Check browser console (F12) for frontend errors
4. Ensure all environment variables are set correctly
5. Verify both backend and frontend are running

---

## 🎉 You're All Set!

Once both servers are running:

1. Open http://localhost:3000 in your browser
2. Navigate to the interview page
3. Start practicing your interviews with AI assistance!

Happy interviewing! 🚀
