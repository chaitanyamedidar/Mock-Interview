# VAPI Voice Interview Integration

This project integrates VAPI (Voice AI Platform) for conducting voice-based mock interviews with real-time transcription and AI feedback.

## How It Works

1. **Voice Interaction**: VAPI handles the voice conversation between the AI interviewer and candidate
2. **Real-time Transcription**: Speech is converted to text using VAPI's transcription service  
3. **ML Analysis**: Transcripts are sent to the backend ML model for analysis
4. **AI Feedback**: The ML model provides structured feedback on interview performance

## VAPI Keys Required

To enable voice functionality, you need to get these keys from [VAPI Dashboard](https://dashboard.vapi.ai/):

### Backend (.env)
```env
VAPI_PUBLIC_KEY=pk_your_actual_public_key
VAPI_PRIVATE_KEY=sk_your_actual_private_key  
VAPI_ASSISTANT_ID=asst_your_actual_assistant_id
VAPI_WEBHOOK_SECRET=your_webhook_secret
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_VAPI_PUBLIC_KEY=pk_your_actual_public_key
NEXT_PUBLIC_VAPI_ASSISTANT_ID=asst_your_actual_assistant_id
```

## Getting VAPI Keys

1. **Sign up** at https://dashboard.vapi.ai/
2. **Create API Keys**:
   - Public Key (pk_xxx) - for frontend
   - Private Key (sk_xxx) - for backend
3. **Create Assistant**:
   - Go to Assistants section
   - Create new assistant for interviews
   - Copy Assistant ID (asst_xxx)
4. **Set Webhook** (optional):
   - Generate a random secret string
   - Configure webhook in assistant settings

## Current Setup Status

⚠️ **Note**: The current VAPI keys in the environment files appear to be placeholders/examples. You need to replace them with actual keys from your VAPI dashboard for the voice functionality to work.

## Features

- **Real-time Voice Conversation**: AI interviewer asks questions via voice
- **Live Transcription**: See your responses transcribed in real-time
- **ML-Powered Feedback**: Get detailed feedback on your interview performance
- **Professional Voice**: Uses ElevenLabs voice synthesis for natural conversation
- **Error Handling**: Graceful fallbacks and error messages

## Voice Interview Flow

1. Start interview → VAPI call begins
2. AI asks questions via voice
3. Candidate responds via voice
4. Real-time transcription displays
5. Response sent to ML model for analysis
6. AI feedback provided
7. Process repeats for next question

## Fallback Mode

If VAPI keys are not configured, the interview will fall back to text-based interaction mode.