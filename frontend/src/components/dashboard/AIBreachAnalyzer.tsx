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
      explanation?: string;
    };
  }) => void;
  initialDescription?: string;
  setConversationSummary: (summary: string) => void;
  classification?: any;
  similarCases?: any[];
  setSimilarCases?: (cases: any[]) => void;
}

export function AIBreachAnalyzer({ onAnalysisComplete, initialDescription = "", setConversationSummary, classification, similarCases, setSimilarCases }: AIBreachAnalyzerProps) {
  const [description, setDescription] = useState(initialDescription);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [caseSummary, setCaseSummary] = useState("");
  const [additionalInput, setAdditionalInput] = useState("");

  // Mock GDPR analysis data
  const mockGDPRAnalysis = [
    {
      article: "Article 5 - Principles",
      status: "Violation",
      description: "Failure to ensure data minimization and purpose limitation"
    },
    {
      article: "Article 32 - Security",
      status: "Violation", 
      description: "Inadequate technical and organizational measures"
    },
    {
      article: "Article 33 - Notification",
      status: "Partial Compliance",
      description: "Delayed notification to supervisory authority"
    }
  ];

  // Auto-analyze if initial description is provided
  useEffect(() => {
    if (initialDescription.trim()) {
      setCaseSummary(initialDescription);
      // Don't auto-analyze if this is from voice agent (contains "GDPR CLASSIFICATION:")
      if (!initialDescription.includes("GDPR CLASSIFICATION:")) {
        setTimeout(() => analyzeBreachCase(), 1000);
      } else {
        // If it contains classification, show a completion message
        toast.success("Voice case gathering completed! Case summary loaded.");
      }
    }
  }, [initialDescription]);

  // Display classification when available and no case summary yet
  useEffect(() => {
    if (classification && !caseSummary) {
      const classificationSummary = `Case Classification Complete:

Case Description: ${classification.case_description || 'Based on voice conversation'}

GDPR Classification:
• Lawfulness of Processing: ${formatClassificationLabel(classification.lawfulness_of_processing)}
• Data Subject Rights Compliance: ${formatClassificationLabel(classification.data_subject_rights_compliance)}
• Risk Management and Safeguards: ${formatClassificationLabel(classification.risk_management_and_safeguards)}
• Accountability and Governance: ${formatClassificationLabel(classification.accountability_and_governance)}

Status: Ready for detailed GDPR compliance analysis.`;
      
      setCaseSummary(classificationSummary);
      setConversationSummary(classificationSummary);
    }
  }, [classification, caseSummary, setConversationSummary]);

  const formatClassificationLabel = (value: string) => {
    return value ? value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Not specified';
  };

  const analyzeBreachCase = async () => {
    // Determine if we should use classification data or description
    const shouldUseClassification = classification && 
      classification.case_description && 
      classification.lawfulness_of_processing &&
      classification.data_subject_rights_compliance &&
      classification.risk_management_and_safeguards &&
      classification.accountability_and_governance;

    if (!shouldUseClassification && !description.trim()) {
      toast.error("Please describe your data breach case");
      return;
    }

    setIsAnalyzing(true);
    
    try {
      let breachImpactResult;

      if (shouldUseClassification) {
        // Use the classification data to call the breach impact API
        const response = await fetch('http://127.0.0.1:5000/api/predict-breach-impact', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            case_description: classification.case_description,
            lawfulness_of_processing: classification.lawfulness_of_processing,
            data_subject_rights_compliance: classification.data_subject_rights_compliance,
            risk_management_and_safeguards: classification.risk_management_and_safeguards,
            accountability_and_governance: classification.accountability_and_governance
          })
        });

        if (!response.ok) {
          throw new Error(`API call failed: ${response.status}`);
        }

        const result = await response.json();
        setSimilarCases(result.similar_cases || []);
        
        if (result.error) {
          throw new Error(result.error);
        }

        // Format the similar cases for display
        const formattedSimilarCases = result.similar_cases.map((caseData: any) => 
          `${caseData.company} - €${(caseData.fine / 1000000).toFixed(1)}M fine (${caseData.similarity}% similar): ${caseData.description.substring(0, 100)}...`
        );

        breachImpactResult = {
          estimatedFine: `€${(result.prediction_result.predicted_fine / 1000000).toFixed(1)}M`,
          riskLevel: result.prediction_result.predicted_fine > 10000000 ? "HIGH" : 
                     result.prediction_result.predicted_fine > 1000000 ? "MEDIUM" : "LOW",
          similarCases: formattedSimilarCases,
          explanation: result.prediction_result.explanation_for_fine
        };

        toast.success("AI breach impact analysis completed successfully");
      } else {
        // Fallback to mock analysis for manual descriptions
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const estimatedFine = description.toLowerCase().includes("personal data") 
          ? "€2.4M - €4.8M" 
          : "€850K - €1.2M";
        
        const riskLevel = description.toLowerCase().includes("sensitive") || description.toLowerCase().includes("health")
          ? "HIGH"
          : "MEDIUM";

        breachImpactResult = {
          estimatedFine,
          riskLevel,
          similarCases: [
            "British Airways - €22M fine for data breach affecting 400K customers",
            "Marriott International - €110M fine for exposing 339M guest records",
            "H&M - €35M fine for employee data monitoring"
          ]
        };

        toast.success("Breach analysis completed successfully");
      }

      onAnalysisComplete({
        gdprCompliance: mockGDPRAnalysis,
        breachImpact: breachImpactResult
      });

      if (!caseSummary) {
        setCaseSummary(shouldUseClassification ? classification.case_description : description);
      } else if (shouldUseClassification) {
        // Update the case summary to indicate analysis is complete
        const updatedSummary = caseSummary + "\n\n=== AI IMPACT ANALYSIS COMPLETE ===";
        setCaseSummary(updatedSummary);
        setConversationSummary(updatedSummary);
      }
      setDescription("");
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(`Analysis failed: ${error instanceof Error ? error.message : 'Please try again.'}`);
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
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-foreground">Case Summary</h3>
                {caseSummary.includes("GDPR CLASSIFICATION:") && (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="font-medium">Voice Agent Complete</span>
                  </div>
                )}
              </div>
              <div className="text-foreground/90 text-sm leading-relaxed space-y-2">
                {caseSummary.split('\n').map((paragraph, index) => (
                  <p key={index} className="text-sm leading-relaxed">
                    {paragraph.split(/(\d+(?:,\d{3})*(?:\.\d+)?|\b(?:GDPR|personal data|sensitive data|data breach|notification|consent|legal basis|encryption|deletion|72 hours|international transfer|DPA|fine|penalty|compliance|violation|risk|HIGH|MEDIUM|LOW|Lawfulness of Processing|Data Subject Rights|Risk Management|Accountability)\b)/gi).map((part, partIndex) => {
                      if (/^\d+(?:,\d{3})*(?:\.\d+)?$/.test(part)) {
                        return <span key={partIndex} className="font-bold text-primary">{part}</span>;
                      }
                      if (/^(?:GDPR|personal data|sensitive data|data breach|notification|consent|legal basis|encryption|deletion|72 hours|international transfer|DPA|fine|penalty|compliance|violation|risk|HIGH|MEDIUM|LOW|Lawfulness of Processing|Data Subject Rights|Risk Management|Accountability)$/i.test(part)) {
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
              <div className="flex items-center justify-between">
                <h4 className="text-md font-medium text-foreground">Add Additional Details</h4>
                {classification && !caseSummary.includes("Analysis Complete") && (
                  <Button 
                    onClick={analyzeBreachCase}
                    disabled={isAnalyzing}
                    className="bg-accent hover:bg-accent/90 text-accent-foreground"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Analyzing Impact...
                      </>
                    ) : (
                      <>
                        <Bot className="h-4 w-4 mr-2" />
                        Analyze Breach Impact
                      </>
                    )}
                  </Button>
                )}
              </div>
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