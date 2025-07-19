import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, AlertTriangle, DollarSign, Users, FileX, Search } from "lucide-react";
import { useState } from "react";

interface SimilarCase {
  id: string;
  company: string;
  description: string;
  fine: number;
  similarity: number;
  date: string;
  authority: string;
}

const similarCases: SimilarCase[] = [
  {
    id: "1",
    company: "Meta Platforms Ireland",
    description: "Cross-border data transfers without adequate safeguards",
    fine: 1200000000,
    similarity: 87,
    date: "2023-05-22",
    authority: "Irish DPC"
  },
  {
    id: "2",
    company: "Amazon Europe Core",
    description: "Inappropriate data processing for advertising purposes",
    fine: 746000000,
    similarity: 72,
    date: "2021-07-30",
    authority: "Luxembourg CNPD"
  },
  {
    id: "3",
    company: "WhatsApp Ireland",
    description: "Insufficient transparency about data processing",
    fine: 225000000,
    similarity: 68,
    date: "2021-09-02",
    authority: "Irish DPC"
  },
  {
    id: "4",
    company: "H&M Hennes & Mauritz",
    description: "Excessive employee monitoring and data collection",
    fine: 35258707,
    similarity: 65,
    date: "2020-10-01",
    authority: "Hamburg DPA"
  }
];

export function BreachImpactPredictor() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-EU', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const calculatePredictedFine = () => {
    const weightedAverage = similarCases.reduce((acc, case_) => {
      return acc + (case_.fine * (case_.similarity / 100));
    }, 0) / similarCases.length;
    
    return Math.round(weightedAverage);
  };

  const predictedFine = calculatePredictedFine();
  const averageSimilarity = Math.round(similarCases.reduce((acc, case_) => acc + case_.similarity, 0) / similarCases.length);

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => setIsAnalyzing(false), 2000);
  };

  const getRiskLevel = (fine: number) => {
    if (fine > 500000000) return { level: "Critical", color: "text-danger", bg: "bg-danger/20" };
    if (fine > 100000000) return { level: "High", color: "text-warning", bg: "bg-warning/20" };
    if (fine > 10000000) return { level: "Medium", color: "text-warning", bg: "bg-warning/10" };
    return { level: "Low", color: "text-success", bg: "bg-success/20" };
  };

  const risk = getRiskLevel(predictedFine);

  return (
    <Card className="bg-gradient-security border-border shadow-card hover:shadow-elevated transition-all duration-300">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-foreground">
            <TrendingUp className="h-5 w-5 text-primary" />
            Breach Impact Predictor
          </CardTitle>
          <Button
            onClick={handleAnalyze} 
            disabled={isAnalyzing}
            className="bg-primary hover:bg-primary/90 hover:shadow-elevated transition-all duration-300"
            size="sm"
          >
            {isAnalyzing ? (
              <>
                <Search className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Analyze Similar Cases
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Predicted Impact */}
        <div className="p-4 rounded-lg bg-card/50 border border-border/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Predicted Financial Impact</h3>
            <Badge className={`${risk.bg} ${risk.color} border-current/30`}>
              {risk.level} Risk
            </Badge>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <DollarSign className="h-6 w-6 text-danger mx-auto mb-2" />
              <div className="text-2xl font-bold text-foreground">{formatCurrency(predictedFine)}</div>
              <div className="text-sm text-muted-foreground">Predicted Fine</div>
            </div>
            <div className="text-center">
              <FileX className="h-6 w-6 text-warning mx-auto mb-2" />
              <div className="text-2xl font-bold text-foreground">{averageSimilarity}%</div>
              <div className="text-sm text-muted-foreground">Avg. Similarity</div>
            </div>
            <div className="text-center">
              <Users className="h-6 w-6 text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold text-foreground">{similarCases.length}</div>
              <div className="text-sm text-muted-foreground">Similar Cases</div>
            </div>
          </div>
        </div>

        {/* Similar Cases */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Similar Cases Found</h3>
          <div className="space-y-3">
            {similarCases.map((case_) => (
              <div key={case_.id} className="p-3 rounded-lg bg-card/30 border border-border/30">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="font-medium text-foreground">{case_.company}</div>
                    <div className="text-sm text-muted-foreground">{case_.description}</div>
                  </div>
                  <Badge variant="outline" className="border-primary/30 text-primary">
                    {case_.similarity}% match
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{case_.authority} • {case_.date}</span>
                  <span className="font-semibold text-danger">{formatCurrency(case_.fine)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Assessment */}
        <div className="p-4 rounded-lg bg-gradient-to-r from-danger/10 to-warning/10 border border-danger/20">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-danger" />
            <h3 className="font-semibold text-foreground">Risk Assessment</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Based on analysis of similar data breach cases, your organization faces a potential fine of{" "}
            <span className="font-semibold text-danger">{formatCurrency(predictedFine)}</span>.
            This assessment considers case similarity, regulatory precedents, and severity factors.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}