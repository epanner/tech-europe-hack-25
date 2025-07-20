import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { OverviewCard } from "@/components/dashboard/OverviewCard";
import { GDPRComplianceCard } from "@/components/dashboard/GDPRComplianceCard";
import { BreachImpactPredictor } from "@/components/dashboard/BreachImpactPredictor";
import { AIBreachAnalyzer } from "@/components/dashboard/AIBreachAnalyzer";
import { VoiceAgent } from "@/components/dashboard/VoiceAgent";
import { Shield, AlertTriangle, TrendingDown, FileX, Users, Clock } from "lucide-react";
import { useEffect, useState } from "react";
import { useCaseGathering } from "@/hooks/useCaseGathering";

const Index = () => {
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [showVoiceAgent, setShowVoiceAgent] = useState(true);
  const [conversationSummary, setConversationSummary] = useState("");
  const [caseClassification, setCaseClassification] = useState<any>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const [similarCases, setSimilarCases] = useState<any[]>([]);

  const { startConversation, sendMessage } = useCaseGathering();

  const [analyticConversation, setAnalyticConversation] = useState<string[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const handleAnalysisComplete = (analysis: any) => {
    setAnalysisResults(analysis);
  };

  const handleConversationComplete = (summary: string, classification: any) => {
    console.log('Conversation complete:', { summary, classification });
    
    setIsTransitioning(true);
    
    if (summary && summary.trim()) {
      setConversationSummary(summary);
    }
    if (classification) {
      setCaseClassification(classification);
      console.log('Classification received:', classification);
    }
    
    // Show transition state briefly before closing voice agent
    setTimeout(() => {
      setShowVoiceAgent(false);
      setIsTransitioning(false);
    }, 500);
  };



  return (
    <>
      {showVoiceAgent && (
        <VoiceAgent onConversationComplete={handleConversationComplete} />
      )}
      
      {isTransitioning && (
        <div className="fixed inset-0 bg-background/95 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-foreground mb-2">Processing Case Classification</h2>
            <p className="text-muted-foreground">Loading your GDPR breach analysis...</p>
          </div>
        </div>
      )}
      
      <div className="min-h-screen bg-background">
        <DashboardHeader />
        
        <main className="container mx-auto px-8 py-12">
          {/* AI Breach Analyzer */}
          <div className="mb-12">
            <AIBreachAnalyzer 
              setConversationSummary={setConversationSummary}
              onAnalysisComplete={handleAnalysisComplete} 
              initialDescription={conversationSummary}
              classification={caseClassification}
              setSimilarCases={setSimilarCases}
              similarCases={similarCases}
            />
          </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          <OverviewCard
            title="Active Data Subjects"
            value="2,847"
            icon={Users}
            description="+12% from last month"
            variant="default"
          />
          <OverviewCard
            title="Open Breach Cases"
            value="3"
            icon={AlertTriangle}
            description="2 high priority"
            variant="warning"
          />
          <OverviewCard
            title="Compliance Score"
            value="87%"
            icon={Shield}
            description="+5% improvement"
            variant="success"
          />
          <OverviewCard
            title="Avg. Response Time"
            value="24h"
            icon={Clock}
            description="Within SLA"
            variant="default"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* GDPR Compliance */}
          <div className="space-y-6">
            <GDPRComplianceCard caseDescription={conversationSummary} />
          </div>
          
          {/* Breach Impact Predictor */}
          <div className="space-y-6">
            <BreachImpactPredictor 
            similarCases={similarCases} setSimilarCases={setSimilarCases} />
          </div>
        </div>
      </main>
    </div>
    </>
  );
};

export default Index;
