import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { OverviewCard } from "@/components/dashboard/OverviewCard";
import { GDPRComplianceCard } from "@/components/dashboard/GDPRComplianceCard";
import { BreachImpactPredictor } from "@/components/dashboard/BreachImpactPredictor";
import { AIBreachAnalyzer } from "@/components/dashboard/AIBreachAnalyzer";
import { VoiceAgent } from "@/components/dashboard/VoiceAgent";
import { Shield, AlertTriangle, TrendingDown, FileX, Users, Clock } from "lucide-react";
import { useState } from "react";

const Index = () => {
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [showVoiceAgent, setShowVoiceAgent] = useState(true);
  const [conversationSummary, setConversationSummary] = useState("");

  const handleAnalysisComplete = (analysis: any) => {
    setAnalysisResults(analysis);
  };

  const handleConversationComplete = (summary: string) => {
    setConversationSummary(summary);
    setShowVoiceAgent(false);
  };

  return (
    <>
      {showVoiceAgent && (
        <VoiceAgent onConversationComplete={handleConversationComplete} />
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
            <BreachImpactPredictor />
          </div>
        </div>
      </main>
    </div>
    </>
  );
};

export default Index;
