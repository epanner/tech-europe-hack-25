import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Bot, Send, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface AIBreachAnalyzerProps {
  onAnalysisComplete: (analysis: {
    gdprCompliance: any[];
    breachImpact: {
      estimatedFine: string;
      riskLevel: string;
      similarCases: string[];
    };
  }) => void;
  initialDescription?: string;
}

export function AIBreachAnalyzer({ onAnalysisComplete, initialDescription = "" }: AIBreachAnalyzerProps) {
  const [description, setDescription] = useState(initialDescription);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [caseSummary, setCaseSummary] = useState("");
  const [additionalInput, setAdditionalInput] = useState("");

  // Auto-analyze if initial description is provided
  useEffect(() => {
    if (initialDescription.trim()) {
      setCaseSummary(initialDescription);
      setTimeout(() => analyzeBreachCase(), 1000);
    }
  }, [initialDescription]);

  const analyzeBreachCase = async () => {
    if (!description.trim()) {
      toast.error("Please describe your data breach case");
      return;
    }

    setIsAnalyzing(true);
    
    try {
      // Simulate AI analysis - in real implementation, this would call your AI service
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock analysis results based on description
      const mockGDPRAnalysis = [
        { article: "Art. 5", status: description.toLowerCase().includes("consent") ? "compliant" : "warning" },
        { article: "Art. 6", status: description.toLowerCase().includes("legal basis") ? "compliant" : "violation" },
        { article: "Art. 13", status: "warning" },
        { article: "Art. 17", status: description.toLowerCase().includes("deletion") ? "compliant" : "violation" },
        { article: "Art. 25", status: "warning" },
        { article: "Art. 32", status: description.toLowerCase().includes("encryption") ? "compliant" : "violation" },
        { article: "Art. 33", status: description.toLowerCase().includes("72 hours") ? "compliant" : "violation" },
        { article: "Art. 34", status: "warning" },
        { article: "Art. 35", status: "compliant" },
        { article: "Art. 44", status: description.toLowerCase().includes("international") ? "warning" : "compliant" }
      ];

      const estimatedFine = description.toLowerCase().includes("personal data") 
        ? "€2.4M - €4.8M" 
        : "€850K - €1.2M";
      
      const riskLevel = description.toLowerCase().includes("sensitive") || description.toLowerCase().includes("health")
        ? "HIGH"
        : "MEDIUM";

      const mockBreachImpact = {
        estimatedFine,
        riskLevel,
        similarCases: [
          "British Airways - €22M fine for data breach affecting 400K customers",
          "Marriott International - €110M fine for exposing 339M guest records",
          "H&M - €35M fine for employee data monitoring"
        ]
      };

      onAnalysisComplete({
        gdprCompliance: mockGDPRAnalysis,
        breachImpact: mockBreachImpact
      });

      toast.success("Breach analysis completed successfully");
      if (!caseSummary) {
        setCaseSummary(description);
      }
      setDescription("");
    } catch (error) {
      toast.error("Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const addAdditionalDetails = async () => {
    if (!additionalInput.trim()) {
      toast.error("Please enter additional details");
      return;
    }

    const updatedDescription = `${caseSummary}\n\nAdditional details: ${additionalInput}`;
    setDescription(updatedDescription);
    setCaseSummary(updatedDescription);
    setAdditionalInput("");
    
    toast.success("Additional details added. Re-analyzing case...");
    setTimeout(() => analyzeBreachCase(), 500);
  };

  return (
    <Card className="bg-gradient-security border-border shadow-card hover:shadow-elevated transition-all duration-300 p-8">
      <div className="flex items-center gap-4 mb-6">
        <Bot className="h-7 w-7 text-primary" />
        <h2 className="text-2xl font-semibold text-foreground">AI Breach Case Analyzer</h2>
      </div>
      
      <div className="space-y-6">
        {caseSummary ? (
          <>
            {/* Case Summary Display */}
            <div className="bg-muted/50 rounded-lg p-6 border border-border">
              <h3 className="text-lg font-medium text-foreground mb-4">Case Summary</h3>
              <div className="text-foreground/90 text-sm leading-relaxed space-y-2">
                {caseSummary.split('\n').map((paragraph, index) => (
                  <p key={index} className="text-sm leading-relaxed">
                    {paragraph.split(/(\d+(?:,\d{3})*(?:\.\d+)?|\b(?:GDPR|personal data|sensitive data|data breach|notification|consent|legal basis|encryption|deletion|72 hours|international transfer|DPA|fine|penalty|compliance|violation|risk|HIGH|MEDIUM|LOW)\b)/gi).map((part, partIndex) => {
                      if (/^\d+(?:,\d{3})*(?:\.\d+)?$/.test(part)) {
                        return <span key={partIndex} className="font-bold text-primary">{part}</span>;
                      }
                      if (/^(?:GDPR|personal data|sensitive data|data breach|notification|consent|legal basis|encryption|deletion|72 hours|international transfer|DPA|fine|penalty|compliance|violation|risk|HIGH|MEDIUM|LOW)$/i.test(part)) {
                        return <span key={partIndex} className="font-semibold text-primary bg-primary/10 px-1 rounded">{part}</span>;
                      }
                      return part;
                    })}
                  </p>
                ))}
              </div>
            </div>
            
            {/* Additional Details Chat Interface */}
            <div className="space-y-4">
              <h4 className="text-md font-medium text-foreground">Add Additional Details</h4>
              <div className="flex gap-3">
                <Textarea
                  placeholder="Add more details about your breach case..."
                  value={additionalInput}
                  onChange={(e) => setAdditionalInput(e.target.value)}
                  className="min-h-[80px] bg-background border-border text-foreground placeholder:text-muted-foreground text-sm"
                  disabled={isAnalyzing}
                />
                <Button 
                  onClick={addAdditionalDetails}
                  disabled={isAnalyzing || !additionalInput.trim()}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground self-end px-6 py-3"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </>
        ) : (
          <>
            <Textarea
              placeholder="Describe your data breach case in detail. Include information about affected data types, number of individuals, security measures in place, notification timelines, and any other relevant details..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[120px] bg-background border-border text-foreground placeholder:text-muted-foreground"
              disabled={isAnalyzing}
            />
            
            <div className="flex justify-end">
              <Button 
                onClick={analyzeBreachCase}
                disabled={isAnalyzing || !description.trim()}
                className="bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Analyze Breach Case
                  </>
                )}
              </Button>
            </div>
          </>
        )}
      </div>
    </Card>
  );
}