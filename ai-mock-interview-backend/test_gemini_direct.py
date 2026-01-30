import asyncio
import sys
import json
sys.path.insert(0, 'D:\\Webdev\\Mock Interview\\ai-mock-interview-backend')

from app.gcp_gemini_service import GCPGeminiService

async def test_gemini_direct():
    try:
        service = GCPGeminiService()
        print("Testing GCP Gemini directly...")
        
        result = await service.analyze_resume(
            resume_text="Software Engineer with 5 years of experience in Python, JavaScript, and cloud technologies.",
            job_description="Looking for a senior software engineer"
        )
        
        print("\n=== GCP Gemini Response ===")
        print(json.dumps(result, indent=2))
        print("\n=== Response Keys ===")
        print(f"Keys: {list(result.keys())}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_direct())
