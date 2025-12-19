import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_id, response_text, interview_type } = body;

    // Validate required fields
    if (!response_text || !interview_type) {
      return NextResponse.json(
        { error: 'Missing required fields: response_text, interview_type' },
        { status: 400 }
      );
    }

    // Call the backend ML analysis endpoint
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/interview/analyze-response`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: session_id || 'voice-session-' + Date.now(),
        question_number: 1,
        response_text,
        interview_type
      })
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Backend analysis error:', errorData);
      return NextResponse.json(
        { error: 'Failed to analyze response with ML model' },
        { status: response.status }
      );
    }

    const feedbackData = await response.json();
    return NextResponse.json(feedbackData);

  } catch (error) {
    console.error('Error in analyze response API:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}