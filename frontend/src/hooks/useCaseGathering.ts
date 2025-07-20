import { useState, useCallback, useRef } from 'react';

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface StreamResponse {
  type: 'conversation_id' | 'message' | 'classification_complete' | 'stream_end' | 'error';
  data: any;
}

interface CaseGatheringState {
  conversationId: string | null;
  messages: ConversationMessage[];
  isStreaming: boolean;
  isReadyToClassify: boolean;
  classification: any | null;
  error: string | null;
  iterationCount: number;
  maxIterations: number;
}

export const useCaseGathering = () => {
  const [state, setState] = useState<CaseGatheringState>({
    conversationId: null,
    messages: [],
    isStreaming: false,
    isReadyToClassify: false,
    classification: null,
    error: null,
    iterationCount: 0,
    maxIterations: 4,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const startConversation = useCallback(async (initialDescription?: string) => {
    try {
      setState(prev => ({
        ...prev,
        isStreaming: true,
        error: null,
        messages: [],
        isReadyToClassify: false,
        classification: null
      }));

      // Add initial user message if provided
      if (initialDescription) {
        setState(prev => ({
          ...prev,
          messages: [{
            role: 'user',
            content: initialDescription,
            timestamp: new Date()
          }]
        }));
      }

      abortControllerRef.current = new AbortController();

      const response = await fetch('http://127.0.0.1:8001/api/start-case-gathering', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          initial_description: initialDescription || '',
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let currentAssistantMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data.trim() === '') continue;

            try {
              const parsed: StreamResponse = JSON.parse(data);
              
              switch (parsed.type) {
                case 'conversation_id':
                  setState(prev => ({
                    ...prev,
                    conversationId: parsed.data
                  }));
                  break;

                case 'message':
                  currentAssistantMessage += parsed.data;
                  // Update the current streaming message
                  setState(prev => {
                    const newMessages = [...prev.messages];
                    const lastMessage = newMessages[newMessages.length - 1];
                    
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.content = currentAssistantMessage;
                    } else {
                      newMessages.push({
                        role: 'assistant',
                        content: currentAssistantMessage,
                        timestamp: new Date()
                      });
                    }
                    
                    return { ...prev, messages: newMessages };
                  });
                  break;

                case 'classification_complete':
                  setState(prev => ({
                    ...prev,
                    isReadyToClassify: true,
                    classification: parsed.data
                  }));
                  break;

                case 'stream_end':
                  setState(prev => ({
                    ...prev,
                    isStreaming: false
                  }));
                  return;

                case 'error':
                  setState(prev => ({
                    ...prev,
                    error: parsed.data,
                    isStreaming: false
                  }));
                  return;
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', data, e);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Stream aborted');
      } else {
        setState(prev => ({
          ...prev,
          error: error.message,
          isStreaming: false
        }));
      }
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!state.conversationId || state.isStreaming) {
      return;
    }

    try {
      setState(prev => ({
        ...prev,
        isStreaming: true,
        error: null,
        iterationCount: prev.iterationCount + 1,
        messages: [
          ...prev.messages,
          {
            role: 'user',
            content: message,
            timestamp: new Date()
          }
        ]
      }));

      abortControllerRef.current = new AbortController();

      const response = await fetch('http://127.0.0.1:8001/api/continue-case-gathering', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: state.conversationId,
          user_response: message,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let currentAssistantMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data.trim() === '') continue;

            try {
              const parsed: StreamResponse = JSON.parse(data);
              
              switch (parsed.type) {
                case 'message':
                  currentAssistantMessage += parsed.data;
                  // Update the current streaming message
                  setState(prev => {
                    const newMessages = [...prev.messages];
                    const lastMessage = newMessages[newMessages.length - 1];
                    
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.content = currentAssistantMessage;
                    } else {
                      newMessages.push({
                        role: 'assistant',
                        content: currentAssistantMessage,
                        timestamp: new Date()
                      });
                    }
                    
                    return { ...prev, messages: newMessages };
                  });
                  break;

                case 'classification_complete':
                  setState(prev => ({
                    ...prev,
                    isReadyToClassify: true,
                    classification: parsed.data
                  }));
                  break;

                case 'stream_end':
                  setState(prev => ({
                    ...prev,
                    isStreaming: false
                  }));
                  return;

                case 'error':
                  setState(prev => ({
                    ...prev,
                    error: parsed.data,
                    isStreaming: false
                  }));
                  return;
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', data, e);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Stream aborted');
      } else {
        setState(prev => ({
          ...prev,
          error: error.message,
          isStreaming: false
        }));
      }
    }
  }, [state.conversationId, state.isStreaming]);

  const endConversation = useCallback(async () => {
    if (!state.conversationId) return;

    try {
      await fetch(`http://127.0.0.1:8001/api/case-gathering/${state.conversationId}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.warn('Failed to end conversation on server:', error);
    }

    // Always clean up local state
    setState({
      conversationId: null,
      messages: [],
      isStreaming: false,
      isReadyToClassify: false,
      classification: null,
      error: null,
      iterationCount: 0,
      maxIterations: 4,
    });

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, [state.conversationId]);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setState(prev => ({
      ...prev,
      isStreaming: false
    }));
  }, []);

  return {
    ...state,
    startConversation,
    sendMessage,
    endConversation,
    stopStreaming,
  };
};

export default useCaseGathering;
