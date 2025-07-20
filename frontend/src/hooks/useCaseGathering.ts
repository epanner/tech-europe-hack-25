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

interface Classifications {
  lawfulness_of_processing: string;
  data_subject_rights_compliance: string;
  risk_management_and_safeguards: string;
  accountability_and_governance: string;
}

interface CaseGatheringState {
  conversationId: string | null;
  messages: ConversationMessage[];
  isStreaming: boolean;
  isReadyToClassify: boolean;
  classification: any | null;
  caseSummary: string | null;
  classifications: Classifications | null;
  conversationComplete: boolean;
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
    caseSummary: null,
    classifications: null,
    conversationComplete: false,
    error: null,
    iterationCount: 0,
    maxIterations: 4,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  // Function to check the latest classification from the backend
  const checkClassificationStatus = useCallback(async (conversationId: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/case-gathering/${conversationId}`);
      if (response.ok) {
        const data = await response.json();
        
        // Update state with comprehensive data from backend
        setState(prev => ({
          ...prev,
          iterationCount: data.iteration_count || prev.iterationCount,
          conversationComplete: data.conversation_complete || false,
          classification: data.classification || prev.classification,
          caseSummary: data.case_summary || prev.caseSummary,
          classifications: data.classifications || prev.classifications,
          isReadyToClassify: data.conversation_complete || prev.isReadyToClassify
        }));
        
        // If conversation is complete, we have classification and summary
        if (data.conversation_complete && data.classification) {
          console.log('Case gathering completed with classification:', data.classification);
          console.log('Case summary:', data.case_summary);
          return {
            classification: data.classification,
            caseSummary: data.case_summary,
            classifications: data.classifications
          };
        }
        
        return data.classification;
      }
    } catch (error) {
      console.warn('Failed to check classification status:', error);
    }
    return null;
  }, []);

  const startConversation = useCallback(async (initialDescription?: string) => {
    let currentConversationId: string | null = null;
    
    try {
      setState(prev => ({
        ...prev,
        isStreaming: true,
        error: null,
        messages: [],
        isReadyToClassify: false,
        classification: null,
        caseSummary: null,
        classifications: null,
        conversationComplete: false
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

      const response = await fetch('http://127.0.0.1:5000/api/start-case-gathering', {
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
                  currentConversationId = parsed.data;
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
                  // Check status immediately when classification is complete
                  if (currentConversationId) {
                    checkClassificationStatus(currentConversationId);
                  }
                  break;

                case 'stream_end':
                  setState(prev => ({
                    ...prev,
                    isStreaming: false
                  }));
                  // Check classification status after stream ends
                  if (currentConversationId) {
                    await checkClassificationStatus(currentConversationId);
                  }
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
  }, [checkClassificationStatus]);

  const sendMessage = useCallback(async (message: string) => {
    if (!state.conversationId || state.isStreaming) {
      return;
    }

    const currentConversationId = state.conversationId;

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

      const response = await fetch('http://127.0.0.1:5000/api/continue-case-gathering', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: currentConversationId,
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
                  // Check status immediately when classification is complete
                  if (currentConversationId) {
                    checkClassificationStatus(currentConversationId);
                  }
                  break;

                case 'stream_end':
                  setState(prev => ({
                    ...prev,
                    isStreaming: false
                  }));
                  // Check classification status after stream ends
                  if (currentConversationId) {
                    await checkClassificationStatus(currentConversationId);
                  }
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
  }, [state.conversationId, state.isStreaming, checkClassificationStatus]);

  const endConversation = useCallback(async () => {
    if (!state.conversationId) return;

    try {
      await fetch(`http://127.0.0.1:5000/api/case-gathering/${state.conversationId}`, {
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
      caseSummary: null,
      classifications: null,
      conversationComplete: false,
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
    checkClassificationStatus,
  };
};

export default useCaseGathering;
