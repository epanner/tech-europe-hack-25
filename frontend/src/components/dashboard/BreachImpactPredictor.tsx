import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, AlertTriangle, DollarSign, Users, FileX, Search } from "lucide-react";
import { useEffect, useState } from "react";
import useBreachPrediction from "@/hooks/useBreachPrediction";

interface SimilarCase {
  id: string;
  company: string;
  description: string;
  fine: number;
  similarity: number;
  explanation_of_similarity: string;
  date: string;
  authority: string;
}

export function BreachImpactPredictor({similarCases, setSimilarCases}: {similarCases: SimilarCase[], setSimilarCases: (cases: SimilarCase[]) => void}) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [predictedFineAmount, setPredictedFineAmount] = useState<number | null>(null);
  const [analysisExplanation, setAnalysisExplanation] = useState<string>("");
  const { predictBreachImpact, loading, error } = useBreachPrediction();

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

  const predictedFine = predictedFineAmount || calculatePredictedFine();
  const averageSimilarity = Math.round(similarCases.reduce((acc, case_) => acc + case_.similarity, 0) / similarCases.length);

  useEffect(() => {
    if (similarCases.length == 0) {
      setIsAnalyzing(true);
    }
      else {
      setIsAnalyzing(false);
      }
  }, [similarCases]);
  
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
                {case_.explanation_of_similarity && (
                  <div className="mt-2 text-xs text-muted-foreground border-t border-border/20 pt-2">
                    <strong>Similarity:</strong> {case_.explanation_of_similarity}
                  </div>
                )}
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
            {analysisExplanation || `Based on analysis of similar data breach cases, your organization faces a potential fine of ${formatCurrency(predictedFine)}. This assessment considers case similarity, regulatory precedents, and severity factors.`}
          </p>
          {error && (
            <div className="mt-2 p-2 bg-danger/10 border border-danger/30 rounded text-xs text-danger">
              Analysis error: {error}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}