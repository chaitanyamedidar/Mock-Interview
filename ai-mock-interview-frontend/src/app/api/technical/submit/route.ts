import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { code, language, snapshots, suspiciousActivity, question, session_id, question_description } = await request.json();

    // Log the submission
    console.log('Technical Interview Submission:', {
      session_id,
      question,
      language,
      codeLength: code.length,
      snapshotCount: snapshots?.length || 0,
      alerts: suspiciousActivity?.length || 0,
    });

    // Forward to backend for LLM evaluation
    try {
      const backendResponse = await fetch('http://localhost:8000/api/v1/technical/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session_id || 'unknown-session',
          code,
          language,
          question_title: question,
          question_description: question_description || '',
        }),
      });

      if (backendResponse.ok) {
        const evaluation = await backendResponse.json();
        return NextResponse.json({
          success: true,
          message: 'Code evaluated successfully',
          ...evaluation,
        });
      } else {
        const errorData = await backendResponse.json().catch(() => ({}));
        console.error('Backend evaluation failed:', errorData);
        // Return basic success even if backend fails
        return NextResponse.json({
          success: true,
          message: 'Code submitted (evaluation pending)',
          session_id,
        });
      }
    } catch (backendError) {
      console.error('Error calling backend:', backendError);
      // Return basic success even if backend is unavailable
      return NextResponse.json({
        success: true,
        message: 'Code submitted (backend unavailable)',
        session_id,
      });
    }
  } catch (error) {
    console.error('Error submitting technical interview:', error);
    return NextResponse.json(
      { error: 'Failed to submit code' },
      { status: 500 }
    );
  }
}
