import os
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv
import json
import logging

load_dotenv()

class VAPIManager:
    """
    Manager class for VAPI voice assistant integration
    """
    
    def __init__(self):
        # Use private key for backend operations
        self.private_key = os.getenv('VAPI_PRIVATE_KEY')
        self.public_key = os.getenv('VAPI_PUBLIC_KEY')
        self.assistant_id = os.getenv('VAPI_ASSISTANT_ID')
        # Fallback to legacy key for backward compatibility
        self.api_key = self.private_key or os.getenv('VAPI_API_KEY')
        self.webhook_secret = os.getenv('VAPI_WEBHOOK_SECRET')
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.base_url = "https://api.vapi.ai"
        
        if not self.api_key:
            logging.warning("VAPI_PRIVATE_KEY not found in environment variables")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_assistant_config(self, session_id: str, interview_type: str, questions: List[str]) -> Dict[str, Any]:
        """
        Create VAPI assistant configuration for interview session
        """
        
        # Generate system prompt based on interview type
        system_prompt = self._generate_system_prompt(interview_type, questions)
        first_message = self._get_first_message(interview_type)
        
        config = {
            "model": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "systemMessage": system_prompt
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Professional female voice
                "stability": 0.5,
                "similarityBoost": 0.8
            },
            "firstMessage": first_message,
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en-US"
            },
            "serverUrl": f"{self.backend_url}/api/vapi/webhook",
            "serverUrlSecret": self.webhook_secret,
            "recordingEnabled": True,
            "endCallMessage": "Thank you for completing the mock interview. Your responses have been analyzed and feedback will be available shortly.",
            "maxDurationSeconds": 3600,  # 1 hour max
            "silenceTimeoutSeconds": 30,
            "functions": [
                {
                    "name": "analyze_response",
                    "description": "Analyze the candidate's response to a question",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "The interview session ID"
                            },
                            "question_number": {
                                "type": "integer",
                                "description": "The current question number"
                            },
                            "response_text": {
                                "type": "string",
                                "description": "The candidate's response text"
                            }
                        },
                        "required": ["session_id", "question_number", "response_text"]
                    }
                },
                {
                    "name": "end_interview",
                    "description": "End the interview session",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "The interview session ID"
                            }
                        },
                        "required": ["session_id"]
                    }
                }
            ]
        }
        
        return config
    
    def _generate_system_prompt(self, interview_type: str, questions: List[str]) -> str:
        """
        Generate system prompt based on interview type and questions
        """
        base_prompt = f"""You are a professional interviewer conducting a {interview_type.replace('_', ' ')} mock interview. Your role is to create a supportive yet professional interview environment.

INSTRUCTIONS:
1. Ask questions one at a time from the provided list in order
2. Wait for complete answers before moving to the next question
3. Provide brief, encouraging acknowledgments between questions ("Thank you", "I see", "Interesting point")
4. If an answer is unclear or too brief, ask ONE follow-up question for clarification
5. Do NOT provide correct answers or extensive feedback during the interview
6. Keep the conversation flowing naturally and professionally
7. After each response, call the analyze_response function to process the answer
8. After all questions are completed, call the end_interview function

QUESTIONS TO ASK (in order):
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(questions))}

CONVERSATION FLOW:
- Start with a warm greeting and brief explanation
- Ask Question 1 and wait for response
- Give brief acknowledgment and ask Question 2
- Continue until all questions are asked
- Thank the candidate and end professionally

TONE: Professional, encouraging, and supportive. Make the candidate feel comfortable while maintaining interview standards."""

        # Add specific guidance based on interview type
        if 'technical' in interview_type:
            base_prompt += """

TECHNICAL INTERVIEW GUIDANCE:
- Listen for technical terminology, algorithms, and system design concepts
- If a candidate mentions code, ask them to explain their thinking process
- For system design questions, encourage them to think about scalability and trade-offs
- Don't correct technical mistakes during the interview"""
        
        elif 'behavioral' in interview_type:
            base_prompt += """

BEHAVIORAL INTERVIEW GUIDANCE:
- Listen for specific examples following the STAR method (Situation, Task, Action, Result)
- If answers are too vague, ask for more specific details about their role and actions
- Encourage quantifiable results where applicable
- Look for leadership, problem-solving, and teamwork examples"""
        
        return base_prompt
    
    def _get_first_message(self, interview_type: str) -> str:
        """
        Generate appropriate first message based on interview type
        """
        messages = {
            'technical_software': "Hello! Welcome to your technical software engineering mock interview. I'll be asking you several questions to assess your technical knowledge and problem-solving skills. Please answer as thoroughly as you can, and feel free to think out loud. Are you ready to begin?",
            'behavioral': "Hello! Welcome to your behavioral mock interview. I'll be asking you questions about your past experiences and how you handle various workplace situations. Please provide specific examples and details about your role and the outcomes. Are you ready to start?",
            'system_design': "Hello! Welcome to your system design mock interview. I'll be presenting you with design challenges where you should think about scalability, trade-offs, and system architecture. Please explain your thought process as you work through each problem. Ready to begin?",
            'general': "Hello! Welcome to your mock interview. I'll be asking you a series of questions to assess your skills and experience. Please answer thoughtfully and provide specific examples where possible. Are you ready to get started?"
        }
        
        return messages.get(interview_type, messages['general'])
    
    def create_assistant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new VAPI assistant with the given configuration
        """
        try:
            response = requests.post(
                f"{self.base_url}/assistant",
                headers=self.headers,
                json=config
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                logging.error(f"Failed to create assistant: {response.status_code} - {response.text}")
                return {'error': f'Failed to create assistant: {response.text}'}
                
        except Exception as e:
            logging.error(f"Error creating assistant: {e}")
            return {'error': str(e)}
    
    def start_call(self, assistant_id: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a phone call with the assistant
        """
        try:
            call_data = {
                "assistantId": assistant_id,
            }
            
            if phone_number:
                call_data["customer"] = {
                    "number": phone_number
                }
            
            response = requests.post(
                f"{self.base_url}/call",
                headers=self.headers,
                json=call_data
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                logging.error(f"Failed to start call: {response.status_code} - {response.text}")
                return {'error': f'Failed to start call: {response.text}'}
                
        except Exception as e:
            logging.error(f"Error starting call: {e}")
            return {'error': str(e)}
    
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming VAPI webhook events
        """
        try:
            message_type = webhook_data.get('type', 'unknown')
            
            if message_type == 'transcript':
                return self._handle_transcript(webhook_data)
            elif message_type == 'function-call':
                return self._handle_function_call(webhook_data)
            elif message_type == 'call-start':
                return self._handle_call_start(webhook_data)
            elif message_type == 'call-end':
                return self._handle_call_end(webhook_data)
            else:
                logging.info(f"Received webhook type: {message_type}")
                return {'status': 'received', 'type': message_type}
                
        except Exception as e:
            logging.error(f"Error handling webhook: {e}")
            return {'error': str(e)}
    
    def _handle_transcript(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle transcript webhook - real-time speech processing
        """
        transcript = data.get('transcript', {})
        text = transcript.get('text', '')
        is_final = transcript.get('isFinal', False)
        
        if is_final and text:
            # Process final transcript
            logging.info(f"Final transcript received: {text}")
            
            # Here you could store the transcript or perform real-time analysis
            # For now, just log it
            
        return {'status': 'processed', 'transcript_processed': is_final}
    
    def _handle_call_start(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call start webhook
        """
        call_id = data.get('call', {}).get('id')
        logging.info(f"Call started: {call_id}")
        
        return {'status': 'call_started', 'call_id': call_id}
    
    def _handle_call_end(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call end webhook
        """
        call_data = data.get('call', {})
        call_id = call_data.get('id')
        duration = call_data.get('duration')
        
        logging.info(f"Call ended: {call_id}, Duration: {duration} seconds")
        
        # Here you could trigger final analysis or cleanup
        
        return {'status': 'call_ended', 'call_id': call_id, 'duration': duration}
    
    def _handle_function_call(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle function call webhook - when assistant calls our functions
        """
        function_call = data.get('functionCall', {})
        function_name = function_call.get('name')
        parameters = function_call.get('parameters', {})
        
        logging.info(f"Function called: {function_name} with params: {parameters}")
        
        if function_name == 'analyze_response':
            # The actual analysis will be handled by the main API
            # This is just acknowledging the function call
            return {
                'result': {
                    'status': 'response_queued_for_analysis',
                    'session_id': parameters.get('session_id'),
                    'question_number': parameters.get('question_number')
                }
            }
        
        elif function_name == 'end_interview':
            # Signal that the interview should be ended
            return {
                'result': {
                    'status': 'interview_ending',
                    'session_id': parameters.get('session_id'),
                    'message': 'Interview completed successfully'
                }
            }
        
        return {'result': {'status': 'function_processed', 'function': function_name}}
    
    def get_call_details(self, call_id: str) -> Dict[str, Any]:
        """
        Get details about a specific call
        """
        try:
            response = requests.get(
                f"{self.base_url}/call/{call_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get call details: {response.status_code}")
                return {'error': 'Failed to get call details'}
                
        except Exception as e:
            logging.error(f"Error getting call details: {e}")
            return {'error': str(e)}
    
    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Validate webhook signature for security
        """
        if not self.webhook_secret:
            logging.warning("Webhook secret not configured")
            return True  # Skip validation if no secret is set
        
        try:
            import hmac
            import hashlib
            
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception as e:
            logging.error(f"Error validating webhook signature: {e}")
            return False

# Usage example and testing
if __name__ == "__main__":
    # Initialize VAPI manager
    vapi_manager = VAPIManager()
    
    # Sample questions
    sample_questions = [
        "Tell me about yourself and your experience with software development",
        "Explain the difference between REST and GraphQL APIs",
        "Describe a challenging technical problem you solved recently"
    ]
    
    # Create assistant configuration
    config = vapi_manager.create_assistant_config(
        session_id="test-session-123",
        interview_type="technical_software",
        questions=sample_questions
    )
    
    print("VAPI Assistant Configuration:")
    print(json.dumps(config, indent=2))
    
    # Test webhook handling
    sample_webhook = {
        "type": "transcript",
        "transcript": {
            "text": "REST API is an architectural style...",
            "isFinal": True
        }
    }
    
    result = vapi_manager.handle_webhook(sample_webhook)
    print(f"\nWebhook handling result: {result}")