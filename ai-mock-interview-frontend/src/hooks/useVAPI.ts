'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import Vapi from '@vapi-ai/web';

export interface VAPIConfig {
  apiKey?: string;
  assistantId?: string;
  assistantConfig?: any; // VAPI assistant configuration object
  metadata?: Record<string, any>; // Metadata to pass to VAPI (session_id, user_id, etc.)
  onCallStart?: () => void;
  onCallEnd?: () => void;
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onMessage?: (message: any) => void;
  onTranscript?: (transcript: string) => void;
  onError?: (error: any) => void;
}

export interface VAPICall {
  start: (metadata?: Record<string, any>) => Promise<void>;
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
  const configRef = useRef(config);

  // Update config ref on every render
  useEffect(() => {
    configRef.current = config;
  });

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
        configRef.current.onCallStart?.();
      });

      vapiRef.current.on('call-end', () => {
        console.log('📞 Call ended');
        setIsCallActive(false);
        setIsSpeaking(false);
        configRef.current.onCallEnd?.();
      });

      vapiRef.current.on('speech-start', () => {
        console.log('🗣️ Speech started');
        setIsSpeaking(true);
        configRef.current.onSpeechStart?.();
      });

      vapiRef.current.on('speech-end', () => {
        console.log('🤐 Speech ended');
        setIsSpeaking(false);
        configRef.current.onSpeechEnd?.();
      });

      vapiRef.current.on('message', (message: any) => {
        console.log('📨 Message:', message);

        // Pass all messages to handler (including role information)
        configRef.current.onMessage?.(message);

        // Also handle legacy transcript callback
        if (message.type === 'transcript' && message.transcript) {
          configRef.current.onTranscript?.(message.transcript);
        }
      });

      vapiRef.current.on('error', (err: any) => {
        console.error('❌ VAPI error:', err);
        let errorMsg = 'Unknown VAPI error';

        if (err?.message) {
          errorMsg = err.message;
        } else if (typeof err === 'string') {
          errorMsg = err;
        } else {
          try {
            errorMsg = JSON.stringify(err, null, 2);
          } catch (e) {
            errorMsg = 'Unserializable VAPI error';
          }
        }

        setError(errorMsg);
        setIsCallActive(false);
        setIsSpeaking(false);
        configRef.current.onError?.(err);
      });

      console.log('✅ VAPI fully initialized and ready!');
    } catch (err: any) {
      console.error('❌ Failed to initialize VAPI:', err);
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
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

  const start = useCallback(async (metadata?: Record<string, any>) => {
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
      if (metadata) {
        console.log('📋 Metadata:', metadata);
      }

      if (assistantId) {
        // Use assistant ID (preferred if backend created one or from .env)
        console.log('✅ Using assistant ID:', assistantId);

        // Prepare overrides to inject dynamic config (questions, prompts) into this specific call
        // This ensures that even if we use a generic Assistant ID from .env, 
        // it gets the specific questions for THIS interview.
        let overrides: any = {};

        if (config.assistantConfig) {
          console.log('📋 Injecting dynamic attributes (model, voice, etc.) into overrides');
          overrides = { ...config.assistantConfig };
        }

        if (metadata || config.metadata) {
          overrides.metadata = metadata || config.metadata;
          // Ensure variableValues is also updated if metadata has context
          // overrides.assistant = { ...overrides.assistant, metadata: overrides.metadata };
        }

        console.log('🚀 Starting call with ID + Overrides');
        // Correct signature: start(assistantId, overrides)
        await vapiRef.current.start(assistantId, overrides);
      } else if (config.assistantConfig) {
        // Use provided assistant configuration (contains questions)
        console.log('✅ Using assistant config from backend with questions');
        const assistantConfig = { ...config.assistantConfig };
        if (metadata || config.metadata) {
          assistantConfig.metadata = metadata || config.metadata;
          console.log('📋 Passing metadata to VAPI:', metadata || config.metadata);
        }
        await vapiRef.current.start(assistantConfig);
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
      const errorMsg = err instanceof Error ? err.message : (typeof err === 'object' ? JSON.stringify(err) : String(err));
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [assistantId, config.assistantConfig, config.metadata]);

  const stop = useCallback(async () => {
    if (!vapiRef.current) return;

    try {
      await vapiRef.current.stop();
    } catch (err: any) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
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