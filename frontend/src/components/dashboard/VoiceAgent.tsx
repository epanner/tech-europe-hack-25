import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Mic, MicOff, Shield, MessageSquare } from "lucide-react";
import { toast } from "sonner";

interface VoiceAgentProps {
  onConversationComplete: (summary: string) => void;
}

export function VoiceAgent({ onConversationComplete }: VoiceAgentProps) {
  const [apiKey, setApiKey] = useState("");
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [conversationSummary, setConversationSummary] = useState("");
  const [showApiKeyInput, setShowApiKeyInput] = useState(true);

  // Load API key from localStorage on component mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem('elevenlabs-api-key');
    if (savedApiKey) {
      setApiKey(savedApiKey);
      setShowApiKeyInput(false);
    }
  }, []);

  const saveApiKey = () => {
    if (apiKey.trim()) {
      localStorage.setItem('elevenlabs-api-key', apiKey);
      setShowApiKeyInput(false);
      toast.success("API key saved successfully");
    }
  };

  const simulateVoiceConversation = async () => {
    if (!apiKey.trim()) {
      toast.error("Please enter your ElevenLabs API key");
      return;
    }

    // Save API key for future use
    localStorage.setItem('elevenlabs-api-key', apiKey);
    
    setIsConnecting(true);
    setShowApiKeyInput(false);
    
    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsConnecting(false);
    setIsConnected(true);
    setIsListening(true);
    
    toast.success("Voice agent connected. Start describing your data breach case.");
    
    // Simulate conversation duration
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    // Simulate conversation end
    const mockSummary = `Data breach incident involving customer database compromise. Approximately 15,000 customer records were potentially accessed including names, email addresses, and encrypted payment information. The breach was discovered through automated monitoring systems and contained within 48 hours. Security measures included immediate password resets and system patches. No sensitive personal data like SSNs or full credit card numbers were exposed. Company has implemented additional encryption and monitoring protocols.`;
    
    setConversationSummary(mockSummary);
    setIsListening(false);
    
    toast.success("Conversation completed. Analyzing your case...");
    
    // Brief delay before transitioning
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    onConversationComplete(mockSummary);
  };

  const skipToTextInput = () => {
    onConversationComplete("");
  };

  const useDemoInput = () => {
    const demoSummary = `Data breach incident involving customer database compromise. Approximately 15,000 customer records were potentially accessed including names, email addresses, and encrypted payment information. The breach was discovered through automated monitoring systems and contained within 48 hours. Security measures included immediate password resets and system patches. No sensitive personal data like SSNs or full credit card numbers were exposed. Company has implemented additional encryption and monitoring protocols.`;
    
    toast.success("Demo input provided. Analyzing case...");
    
    setTimeout(() => {
      onConversationComplete(demoSummary);
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-background flex items-center justify-center p-6 z-50">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-4 mb-6">
            <Shield className="h-16 w-16 text-primary" />
            <div>
              <h1 className="text-4xl font-bold text-foreground mb-2">DataGuard Pro</h1>
              <p className="text-xl text-muted-foreground">AI-Powered Data Breach Assistant</p>
            </div>
          </div>
          <p className="text-lg text-foreground/80 max-w-lg mx-auto">
            Describe your data breach case to our AI voice agent for immediate analysis and compliance guidance.
          </p>
        </div>

        {/* Main Interface */}
        <Card className="bg-card border-border shadow-2xl p-10">
          {showApiKeyInput && !isConnected ? (
            <div className="space-y-8">
              <div className="text-center">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Connect Voice Agent</h2>
                <p className="text-muted-foreground mb-6">
                  Enter your ElevenLabs API key to enable voice interaction, or skip to use text input.
                </p>
              </div>
              
              <div className="space-y-4">
                <Input
                  type="password"
                  placeholder="Enter your ElevenLabs API key..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="text-center text-lg py-6"
                />
                
                <div className="flex gap-4">
                  <Button 
                    onClick={simulateVoiceConversation}
                    disabled={!apiKey.trim() || isConnecting}
                    className="flex-1 py-6 text-lg"
                    size="lg"
                  >
                    {isConnecting ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Mic className="h-5 w-5 mr-3" />
                        Start Voice Session
                      </>
                    )}
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    onClick={skipToTextInput}
                    className="py-6 text-lg"
                    size="lg"
                  >
                    <MessageSquare className="h-5 w-5 mr-3" />
                    Skip to Text
                  </Button>
                </div>
              </div>
              
              <div className="text-center text-sm text-muted-foreground">
                <p>Need an API key? Visit <a href="https://elevenlabs.io" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">ElevenLabs.io</a></p>
              </div>
            </div>
          ) : !showApiKeyInput && !isConnected ? (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Ready to Connect</h2>
                <p className="text-muted-foreground mb-6">
                  Start your voice session or use demo input for testing.
                </p>
              </div>
              
              <div className="space-y-3">
                <Button 
                  onClick={simulateVoiceConversation}
                  disabled={isConnecting}
                  className="w-full py-6 text-lg"
                  size="lg"
                >
                  {isConnecting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Mic className="h-5 w-5 mr-3" />
                      Start Voice Session
                    </>
                  )}
                </Button>
                
                <div className="flex gap-3">
                  <Button 
                    variant="outline" 
                    onClick={useDemoInput}
                    className="flex-1 py-4 text-base"
                    size="lg"
                  >
                    Demo Input
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    onClick={skipToTextInput}
                    className="flex-1 py-4 text-base"
                    size="lg"
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Skip to Text
                  </Button>
                </div>
              </div>
            </div>
          ) : isConnected ? (
            <div className="text-center space-y-8">
              <div className="space-y-4">
                <div className={`w-32 h-32 mx-auto rounded-full border-4 ${isListening ? 'border-primary animate-pulse bg-primary/20' : 'border-muted bg-muted/20'} flex items-center justify-center`}>
                  {isListening ? (
                    <Mic className="h-12 w-12 text-primary" />
                  ) : (
                    <MicOff className="h-12 w-12 text-muted-foreground" />
                  )}
                </div>
                
                <h2 className="text-2xl font-semibold text-foreground">
                  {isListening ? "Listening..." : "Processing..."}
                </h2>
                
                <p className="text-muted-foreground max-w-md mx-auto">
                  {isListening 
                    ? "Please describe your data breach incident in detail. Include affected data types, timeline, and any security measures taken."
                    : "Analyzing your case and preparing compliance assessment..."
                  }
                </p>
              </div>
              
              {isListening && (
                <>
                  <div className="flex justify-center space-x-2 mb-6">
                    <div className="w-2 h-8 bg-primary/60 rounded-full animate-pulse"></div>
                    <div className="w-2 h-12 bg-primary/80 rounded-full animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-6 bg-primary/60 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-10 bg-primary/70 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                  </div>
                  
                  <Button 
                    variant="outline" 
                    onClick={useDemoInput}
                    className="mx-auto block"
                  >
                    Demo Input
                  </Button>
                </>
              )}
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}