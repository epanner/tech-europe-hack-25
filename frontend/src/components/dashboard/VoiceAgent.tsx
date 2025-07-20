import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Mic, MicOff, Shield, X, Bot, User } from "lucide-react";
import { toast } from "sonner";
import { useCaseGathering } from "@/hooks/useCaseGathering";
import { ScrollArea } from "@/components/ui/scroll-area";

interface VoiceAgentProps {
  onConversationComplete: (summary: string, classification: any) => void;
}

export function VoiceAgent({ onConversationComplete }: VoiceAgentProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [transcribedText, setTranscribedText] = useState<string>("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Use case gathering hook
  const {
    messages,
    isStreaming,
    isReadyToClassify,
    classification,
    conversationId,
    startConversation,
    sendMessage,
    endConversation,
    checkClassificationStatus,
    error: gatheringError
  } = useCaseGathering();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle classification complete
  useEffect(() => {
    if (isReadyToClassify && classification) {
      // Create a comprehensive case summary from the conversation
      const userMessages = messages.filter(m => m.role === 'user').map(m => m.content);
      const assistantMessages = messages.filter(m => m.role === 'assistant').map(m => m.content);
      
      // Use classification description if available, otherwise compile from conversation
      let caseDescription = classification.case_description;
      if (!caseDescription || caseDescription === "Data breach incident based on conversation history") {
        caseDescription = userMessages.join('\n\n');
      }
      
      // Create a comprehensive summary that includes both the case details and classification
      const completeSummary = `CASE SUMMARY:
${caseDescription}

GDPR CLASSIFICATION:
• Lawfulness of Processing: ${classification.lawfulness_of_processing}
• Data Subject Rights Compliance: ${classification.data_subject_rights_compliance}
• Risk Management and Safeguards: ${classification.risk_management_and_safeguards}
• Accountability and Governance: ${classification.accountability_and_governance}

CONVERSATION COMPLETE: Case gathering finished with ${messages.length} exchanges.`;
      
      console.log('Classification complete:', classification);
      console.log('Case summary:', completeSummary);
      
      // Close the voice agent and pass the data
      toast.success("🎉 Case gathering complete! Closing voice agent...");
      
      // Small delay to show the completion message before closing
      setTimeout(() => {
        onConversationComplete(completeSummary, classification);
      }, 1500);
    }
  }, [isReadyToClassify, classification, messages, onConversationComplete]);

  // Periodic check to ensure we don't miss the classification due to streaming issues
  useEffect(() => {
    if (conversationId && !isReadyToClassify && !isStreaming) {
      // Check classification status 1 second after streaming stops
      const timeoutId = setTimeout(async () => {
        await checkClassificationStatus(conversationId);
      }, 1000);

      return () => clearTimeout(timeoutId);
    }
  }, [conversationId, isReadyToClassify, isStreaming, checkClassificationStatus]);

  // Get API key from env safely
  useEffect(() => {
    try {
      const key = import.meta.env.VITE_ELEVENLABS_API_KEY;
      setApiKey(key || null);
    } catch (err) {
      console.error("Error accessing environment variable:", err);
      setApiKey(null);
    }
  }, []);

  const startRecording = async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/wav' });
      audioChunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await transcribeAudio(audioBlob);
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch (err: any) {
      // Fallback to default format if wav is not supported
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        audioChunksRef.current = [];
        recorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data);
        };
        recorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp4' });
          await transcribeAudio(audioBlob);
        };
        mediaRecorderRef.current = recorder;
        recorder.start();
        setIsRecording(true);
      } catch (fallbackErr: any) {
        setError("Microphone access denied or not available.");
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true);
    setError(null);
    try {
      if (!apiKey) {
        setError("ElevenLabs API key is not set in the environment.");
        setIsTranscribing(false);
        return;
      }
      
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');
      formData.append('model_id', 'scribe_v1_experimental');
      formData.append('optimize_streaming_latency', '0');
      
      const response = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {
        method: 'POST',
        headers: {
          'xi-api-key': apiKey,
          // Don't set Content-Type header - let the browser set it with boundary for FormData
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('ElevenLabs API error:', response.status, errorText);
        setError(`Transcription failed (${response.status}). Check your API key and audio format.`);
        setIsTranscribing(false);
        return;
      }
      
      const data = await response.json();
      if (data && data.text) {
        // Clean the transcript by removing sound descriptions
        let cleanText = data.text;
        
        // Remove common sound descriptions
        const soundPatterns = [
          /\[.*?\]/g, // Remove anything in brackets
          /\(.*?\)/g, // Remove anything in parentheses
          /\b(um|uh|ah|er|hmm|mm|mhm|uh-huh|uh-uh)\b/gi, // Remove filler words
          /\b(silence|background noise|music|sound|noise|static|breathing|coughing|sneezing|clearing throat)\b/gi, // Remove sound descriptions
        ];
        
        soundPatterns.forEach(pattern => {
          cleanText = cleanText.replace(pattern, '');
        });
        
        // Clean up extra whitespace
        cleanText = cleanText.replace(/\s+/g, ' ').trim();
        
        if (cleanText) {
          setTranscribedText(cleanText);
          
          // If no conversation started yet, start one with the transcribed text
          if (!conversationId) {
            await startConversation(cleanText);
          } else {
            // Continue the conversation with the transcribed text
            await sendMessage(cleanText);
          }
          
          toast.success("Voice input processed!");
        } else {
          setError("No meaningful text could be extracted from the audio.");
        }
      } else {
        setError("No transcript returned from ElevenLabs.");
      }
    } catch (err: any) {
      console.error('Transcription error:', err);
      setError("Error during transcription.");
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleClose = async () => {
    if (conversationId) {
      await endConversation();
    }
    onConversationComplete("", null);
  };

  return (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm flex items-center justify-center p-6 z-50">
      <div className="w-full max-w-4xl h-full max-h-[90vh] flex flex-col">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-4 mb-4">
            <img src="/logo.png" alt="Data Guard Pro Logo" className="h-12 w-auto" />
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-1">DataGuard Pro</h1>
              <p className="text-lg text-muted-foreground">AI-Powered GDPR Case Gathering</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="ml-auto"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-sm text-foreground/80 max-w-2xl mx-auto">
            Use voice input to describe your data breach case. Our AI assistant will gather detailed information through conversation.
          </p>
        </div>
        
        <Card className="bg-card border-border shadow-2xl flex-1 flex flex-col overflow-hidden">
          {/* Conversation Area */}
          <div className="flex-1 flex flex-col min-h-0">
            {messages.length > 0 ? (
              <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex gap-3 ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`flex gap-3 max-w-[80%] ${
                          message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                        }`}
                      >
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                          {message.role === 'user' ? (
                            <User className="h-4 w-4" />
                          ) : (
                            <Bot className="h-4 w-4 text-primary" />
                          )}
                        </div>
                        <div
                          className={`rounded-lg px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted text-foreground'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap leading-relaxed">
                            {message.content}
                          </p>
                          <p className="text-xs mt-1 opacity-60">
                            {message.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {isStreaming && (
                    <div className="flex gap-3 justify-start">
                      <div className="flex gap-3 max-w-[80%]">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary animate-pulse" />
                        </div>
                        <div className="bg-muted text-foreground rounded-lg px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary"></div>
                            <span className="text-sm">Assistant is thinking...</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
            ) : (
              <div className="flex-1 flex items-center justify-center p-6">
                <div className="text-center">
                  <Bot className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg text-muted-foreground mb-2">Ready to start case gathering</p>
                  <p className="text-sm text-muted-foreground/80">
                    Click the microphone button and describe your data breach case
                  </p>
                </div>
              </div>
            )}
          </div>
          
          {/* Voice Input Controls */}
          <div className="border-t border-border p-6">
            <div className="flex flex-col items-center gap-4">
              {/* Status Messages */}
              {(error || gatheringError) && (
                <div className="text-destructive text-sm text-center">
                  {error || gatheringError}
                </div>
              )}
              
              {transcribedText && (
                <div className="bg-muted/50 rounded-lg p-3 text-sm text-center max-w-2xl">
                  <span className="text-muted-foreground">Last transcribed: </span>
                  <span className="text-foreground">{transcribedText}</span>
                </div>
              )}

              {isReadyToClassify && classification && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center max-w-2xl">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
                    <p className="text-sm text-green-700 font-medium">
                      🎉 Case Classification Complete!
                    </p>
                  </div>
                  <div className="text-xs text-green-600 space-y-1">
                    <p>✅ Lawfulness of Processing: <span className="font-medium">{classification.lawfulness_of_processing}</span></p>
                    <p>✅ Data Subject Rights: <span className="font-medium">{classification.data_subject_rights_compliance}</span></p>
                    <p>✅ Risk Management: <span className="font-medium">{classification.risk_management_and_safeguards}</span></p>
                    <p>✅ Accountability: <span className="font-medium">{classification.accountability_and_governance}</span></p>
                  </div>
                  <p className="text-xs text-green-600 mt-2 font-medium">
                    Closing voice agent and loading case summary...
                  </p>
                </div>
              )}
              
              {/* Voice Input Button */}
              <div className="flex items-center gap-4">
                {!isRecording && !isTranscribing && !isReadyToClassify && (
                  <Button 
                    onClick={startRecording} 
                    className="w-40 h-12 text-base flex items-center justify-center"
                    disabled={isStreaming}
                  >
                    <Mic className="h-5 w-5 mr-2" /> 
                    {conversationId ? 'Continue' : 'Start Recording'}
                  </Button>
                )}
                
                {isRecording && !isReadyToClassify && (
                  <Button 
                    onClick={stopRecording} 
                    className="w-40 h-12 text-base flex items-center justify-center bg-destructive hover:bg-destructive/90"
                  >
                    <MicOff className="h-5 w-5 mr-2" /> Stop Recording
                  </Button>
                )}
                
                {isTranscribing && (
                  <div className="text-primary text-base flex items-center gap-2">
                    <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></span>
                    Transcribing...
                  </div>
                )}

                {isReadyToClassify && (
                  <div className="text-green-600 text-base flex items-center gap-2">
                    <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
                    Classification Complete
                  </div>
                )}
              </div>
              
              {/* Progress Indicator */}
              {conversationId && (
                <div className="text-xs text-muted-foreground text-center">
                  <p>Conversation in progress • {messages.length} exchanges</p>
                  {isReadyToClassify ? (
                    <p className="text-green-600 font-medium">✅ Classification complete - Preparing case summary</p>
                  ) : (
                    <p className="text-primary">
                      {messages.length >= 4 ? '⚡ Final exchange - Classification imminent' : 
                       messages.length >= 3 ? '⚠️ Almost complete' : 
                       'Gathering information...'}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}