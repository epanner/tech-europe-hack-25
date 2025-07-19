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
  setConversationSummary: (summary: string) => void;
}

export function AIBreachAnalyzer({ onAnalysisComplete, initialDescription = "", setConversationSummary }: AIBreachAnalyzerProps) {
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
        {
          classification: description.toLowerCase().includes("consent") ? "low" : "medium",
          description: "Lawfulness, fairness, and transparency.",
          name: "Article 5",
          reason: "A breach might indicate a lack of transparency or fairness in data processing, which is a low risk if other controls are in place.",
          summary: "Establishes principles for lawful, fair, and transparent processing of personal data."
        },
        {
          classification: description.toLowerCase().includes("legal basis") ? "low" : "high",
          description: "Lawfulness of processing.",
          name: "Article 6",
          reason: "A breach might imply that data processing wasn't lawful or secured, which can signify a high risk of not having a lawful basis for processing data.",
          summary: "Establishes the lawful bases for processing personal data, including consent and contracts."
        },
        {
          classification: "low",
          description: "Transparency requirements.",
          name: "Article 13",
          reason: "A breach here may mean data subjects are not properly informed, but the risk is low if other requirements are met.",
          summary: "Requires providing information to data subjects about processing activities."
        },
        {
          classification: description.toLowerCase().includes("deletion") ? "low" : "high",
          description: "Right to be forgotten.",
          name: "Article 17",
          reason: "A breach may mean erasure requests are not honored, which is a high risk for non-compliance.",
          summary: "Grants individuals the right to have their personal data erased under certain conditions."
        },
        {
          classification: "medium",
          description: "Privacy by design and default.",
          name: "Article 25",
          reason: "A breach may indicate insufficient privacy measures in system design, a medium risk for ongoing compliance.",
          summary: "Requires data protection measures to be integrated into processing activities and systems."
        },
        {
          classification: description.toLowerCase().includes("encryption") ? "low" : "high",
          description: "Technical and organizational measures.",
          name: "Article 32",
          reason: "A breach may mean security controls are lacking, but if other controls are strong, risk is low.",
          summary: "Mandates appropriate security measures for processing personal data."
        },
        {
          classification: description.toLowerCase().includes("72 hours") ? "low" : "high",
          description: "Notification to supervisory authority.",
          name: "Article 33",
          reason: "A breach may not be reported in time, which is a high risk for regulatory penalties.",
          summary: "Requires notification of personal data breaches to authorities within 72 hours."
        },
        {
          classification: "high",
          description: "High-risk breach communication.",
          name: "Article 34",
          reason: "A breach may not be communicated to data subjects, which is a high risk for trust and compliance.",
          summary: "Requires communication of high-risk breaches to affected data subjects."
        },
        {
          classification: "low",
          description: "DPIA requirements.",
          name: "Article 35",
          reason: "A breach may mean DPIAs are not conducted, but risk is low if other controls are strong.",
          summary: "Requires Data Protection Impact Assessments for high-risk processing activities."
        },
        {
          classification: description.toLowerCase().includes("international") ? "medium" : "low",
          description: "Cross-border data transfers.",
          name: "Article 44",
          reason: "A breach may mean international transfers are not properly safeguarded, a medium risk for compliance.",
          summary: "Regulates transfers of personal data outside the EU/EEA."
        }
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
    setConversationSummary(updatedDescription);
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