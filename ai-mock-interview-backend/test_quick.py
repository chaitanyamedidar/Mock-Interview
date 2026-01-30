import asyncio
import sys
import json
sys.path.insert(0, 'D:\\Webdev\\Mock Interview\\ai-mock-interview-backend')

from app.gcp_gemini_service import GCPGeminiService

async def test():
    service = GCPGeminiService()
    print("Testing resume analysis...")
    
    result = await service.analyze_resume(
        "Software Engineer with 5 years of experience in Python, JavaScript, React, Node.js, AWS, Docker, and Kubernetes. Built scalable microservices serving millions of users.",
        "Looking for Senior Software Engineer with cloud experience"
    )
    
    print("\n=== SUCCESS ===")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
