import asyncio
import sys
sys.path.insert(0, 'D:\\Webdev\\Mock Interview\\ai-mock-interview-backend')

from app.resume_service import ATSResumeAnalyzer

async def test_resume_analysis():
    try:
        analyzer = ATSResumeAnalyzer()
        print(f"Analyzer initialized. Using Gemini: {analyzer.use_gemini}")
        
        # Test with simple resume text
        result = await analyzer.analyze_resume(
            resume_text="Software Engineer with 5 years of experience in Python, JavaScript, and cloud technologies. Built scalable web applications.",
            job_description="Looking for a senior software engineer",
            target_role="Senior Software Engineer"
        )
        
        print("Analysis successful!")
        print(f"ATS Score: {result.get('ats_score', 'N/A')}")
        print(f"Summary: {result.get('summary', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_resume_analysis())
