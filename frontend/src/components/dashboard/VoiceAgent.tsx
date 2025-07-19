import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Mic, MicOff, Shield } from "lucide-react";
import { toast } from "sonner";

interface VoiceAgentProps {
  onConversationComplete: (summary: string) => void;
}

export function VoiceAgent({ onConversationComplete }: VoiceAgentProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [conversationSummary, setConversationSummary] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

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
        
        setConversationSummary(cleanText);
        onConversationComplete(cleanText);
        toast.success("Transcription complete!");
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

  return (
    <div className="fixed inset-0 bg-background flex items-center justify-center p-6 z-50">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-4 mb-6">
            <img src="/logo.png" alt="Data Guard Pro Logo" className="h-16 w-auto" />
            <div>
              <h1 className="text-4xl font-bold text-foreground mb-2">DataGuard Pro</h1>
              <p className="text-xl text-muted-foreground">AI-Powered Data Breach Assistant</p>
            </div>
          </div>
          <p className="text-lg text-foreground/80 max-w-lg mx-auto">
            Describe your data breach case to our AI voice agent for immediate analysis and compliance guidance.
          </p>
        </div>
        <Card className="bg-card border-border shadow-2xl p-10">
          <div className="flex flex-col items-center gap-6">
            {!isRecording && !isTranscribing && (
              <Button onClick={startRecording} className="w-48 h-14 text-lg flex items-center justify-center">
                <Mic className="h-6 w-6 mr-2" /> Start Recording
              </Button>
            )}
            {isRecording && (
              <Button onClick={stopRecording} className="w-48 h-14 text-lg flex items-center justify-center bg-danger hover:bg-danger/90">
                <MicOff className="h-6 w-6 mr-2" /> Stop Recording
              </Button>
            )}
            {isTranscribing && (
              <div className="text-primary text-lg flex items-center gap-2">
                <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></span>
                Transcribing...
              </div>
            )}
            {error && <div className="text-danger text-sm mt-2">{error}</div>}
            {conversationSummary && (
              <div className="bg-muted/50 rounded-lg p-6 border border-border mt-4 text-left">
                <h3 className="text-lg font-medium text-foreground mb-2">Transcript</h3>
                <p className="text-foreground/90 text-base leading-relaxed whitespace-pre-line">{conversationSummary}</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}