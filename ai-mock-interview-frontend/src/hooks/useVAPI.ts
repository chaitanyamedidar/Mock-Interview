'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import Vapi from '@vapi-ai/web';

export interface VAPIConfig {
  apiKey?: string;
  assistantId?: string;
  assistantConfig?: any; // VAPI assistant configuration object
  onCallStart?: () => void;
  onCallEnd?: () => void;
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onMessage?: (message: any) => void;
  onTranscript?: (transcript: string) => void;
  onError?: (error: any) => void;
}

export interface VAPICall {
  start: () => Promise<void>;
  stop: () => Promise<void>;
  send: (message: any) => void;
  isCallActive: boolean;
  isSpeaking: boolean;
  isLoading: boolean;
  transcript: string;
  error: string | null;
}

export function useVAPI(config: Partial<VAPIConfig> = {}): VAPICall {
  const [isCallActive, setIsCallActive] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const vapiRef = useRef<Vapi | null>(null);
  
  // Use environment variables or provided values
  const apiKey = config.apiKey || process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY;
  const assistantId = config.assistantId || process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID;

  // Initialize VAPI
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (vapiRef.current) return; // Already initialized

    if (!apiKey) {
      const errorMsg = 'VAPI API key not set. Please add NEXT_PUBLIC_VAPI_PUBLIC_KEY to your .env.local file.';
      console.error('❌', errorMsg);
      console.log('💡 Check your .env.local file');
      setError(errorMsg);
      return;
    }

    try {
      console.log('🔧 Initializing VAPI SDK...');
      console.log('📝 API Key:', apiKey.substring(0, 15) + '...');
      
      // Create VAPI instance
      vapiRef.current = new Vapi(apiKey);
      console.log('✅ VAPI instance created successfully');
      
      // Set up event listeners
      vapiRef.current.on('call-start', () => {
        console.log('📞 Call started');
        setIsCallActive(true);
        setError(null);
        config.onCallStart?.();
      });

      vapiRef.current.on('call-end', () => {
        console.log('📞 Call ended');
        setIsCallActive(false);
        setIsSpeaking(false);
        config.onCallEnd?.();
      });

      vapiRef.current.on('speech-start', () => {
        console.log('🗣️ Speech started');
        setIsSpeaking(true);
        config.onSpeechStart?.();
      });

      vapiRef.current.on('speech-end', () => {
        console.log('🤐 Speech ended');
        setIsSpeaking(false);
        config.onSpeechEnd?.();
      });

      vapiRef.current.on('message', (message: any) => {
        console.log('📨 Message:', message);
        
        // Pass all messages to handler (including role information)
        config.onMessage?.(message);
        
        // Also handle legacy transcript callback
        if (message.type === 'transcript' && message.transcript) {
          config.onTranscript?.(message.transcript);
        }
      });

      vapiRef.current.on('error', (err: any) => {
        console.error('❌ VAPI error:', err);
        const errorMsg = err?.message || err?.error || 'Unknown VAPI error';
        setError(errorMsg);
        setIsCallActive(false);
        setIsSpeaking(false);
        config.onError?.(err);
      });
      
      console.log('✅ VAPI fully initialized and ready!');
    } catch (err: any) {
      console.error('❌ Failed to initialize VAPI:', err);
      setError(err.message || 'Failed to initialize VAPI SDK');
    }

    // Cleanup
    return () => {
      if (vapiRef.current) {
        try {
          vapiRef.current.stop();
          console.log('🧹 VAPI cleaned up');
        } catch (err) {
          console.error('Error stopping VAPI on cleanup:', err);
        }
      }
    };
  }, [apiKey]);

  const start = useCallback(async () => {
    if (!vapiRef.current) {
      setError('VAPI SDK not initialized. Please check your API key.');
      console.error('❌ VAPI not initialized');
      return;
    }

    setIsLoading(true);
    try {
      console.log('🚀 Starting VAPI call...');
      console.log('📋 Assistant ID:', assistantId || 'No assistant ID');
      console.log('📋 Has Assistant Config:', !!config.assistantConfig);
      
      if (assistantId) {
        // Use assistant ID (preferred if backend created one)
        console.log('✅ Using assistant ID from backend');
        await vapiRef.current.start(assistantId);
      } else if (config.assistantConfig) {
        // Use provided assistant configuration (contains questions)
        console.log('✅ Using assistant config from backend with questions');
        await vapiRef.current.start(config.assistantConfig);
      } else {
        // Fallback: Use basic inline assistant configuration
        console.log('⚠️ Using fallback assistant config (no questions)');
        const fallbackConfig = {
          model: {
            provider: "openai" as const,
            model: "gpt-3.5-turbo",
            temperature: 0.7,
            messages: [{
              role: "system" as const,
              content: "You are an AI interviewer conducting a mock interview. Ask one question at a time, listen to the candidate's response, and provide constructive feedback. Keep the conversation natural and engaging."
            }]
          },
          voice: {
            provider: "11labs" as const,
            voiceId: "21m00Tcm4TlvDq8ikWAM"
          },
          firstMessage: "Hello! I'm your AI interviewer. I'm excited to conduct this mock interview with you today. Let's begin with our first question.",
          transcriber: {
            provider: "deepgram" as const,
            model: "nova-2" as const,
            language: "en-US" as const
          }
        };
        
        await vapiRef.current.start(fallbackConfig as any);
      }
      
      console.log('✅ VAPI call started successfully');
    } catch (err: any) {
      console.error('❌ Failed to start VAPI call:', err);
      setError(err.message || 'Failed to start call');
    } finally {
      setIsLoading(false);
    }
  }, [assistantId, config.assistantConfig]);

  const stop = useCallback(async () => {
    if (!vapiRef.current) return;

    try {
      await vapiRef.current.stop();
    } catch (err: any) {
      setError(err.message || 'Failed to stop call');
      console.error('Failed to stop VAPI call:', err);
    }
  }, []);

  const send = useCallback((message: any) => {
    if (!vapiRef.current) {
      console.error('❌ Cannot send message: VAPI not initialized');
      return;
    }

    try {
      vapiRef.current.send(message);
      console.log('📤 Message sent to VAPI:', message);
    } catch (err: any) {
      console.error('❌ Failed to send message to VAPI:', err);
    }
  }, []);

  return {
    start,
    stop,
    send,
    isCallActive,
    isSpeaking,
    isLoading,
    transcript,
    error
  };
}