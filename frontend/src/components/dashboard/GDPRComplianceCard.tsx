import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { CheckCircle, AlertCircle, XCircle, FileText, ChevronDown } from "lucide-react";
import { useEffect, useState } from "react";

type GDPRArticle = {
  classification: "high" | "medium" | "low";
  description: string;
  name: string;
  reason: string;
  summary: string;
};

type ClassificationColor = {
  [key in GDPRArticle["classification"]]: string;
};

const classificationColor: ClassificationColor = {
  high: "text-danger bg-danger/10 border-danger/30",
  medium: "text-warning bg-warning/10 border-warning/30",
  low: "text-success bg-success/10 border-success/30"
};

const classificationLabel: ClassificationColor = {
  high: "High Risk",
  medium: "Medium Risk",
  low: "Low Risk"
};

export function GDPRComplianceCard({ caseDescription }: { caseDescription: string }) {
  const [gdprArticles, setGdprArticles] = useState<GDPRArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseDescription) return;
    setLoading(true);
    setError(null);
    console.log("Fetching GDPR compliance assessment for case:", caseDescription);
    fetch("http://localhost:5000/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_description: caseDescription })
    })
      .then(async (res) => {
        console.log("Response status:", res.status);
        if (!res.ok) {
          console.log(res);
        };
        const data = await res.json();
        setGdprArticles(data.paragraphs || []);
      })
      .catch((err) => {
        console.log("Error fetching GDPR compliance assessment:");
        console.error(err);
        console.log(err);
        setError(err.message)
      })
      .finally(() => setLoading(false));
  }, [caseDescription]);

  return (
    <Card className="bg-gradient-security border-border shadow-card hover:shadow-elevated transition-all duration-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-foreground">
          <FileText className="h-5 w-5 text-primary" />
          GDPR Compliance Assessment
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center text-muted-foreground py-8">Loading assessment...</div>
        ) : error ? (
          <div className="text-center text-danger py-8">{error}</div>
        ) : (
          <Accordion type="multiple" className="space-y-2">
            {gdprArticles.map((article) => (
              <AccordionItem 
                key={article.name}
                value={article.name}
                className="border border-border/50 rounded-lg px-3 data-[state=open]:shadow-inner-glow"
              >
                <AccordionTrigger className="hover:no-underline py-3">
                  <div className="flex items-center justify-between w-full pr-4">
                    <div className="text-left">
                      <div className="font-medium text-foreground">{article.name}</div>
                      <div className="text-sm text-muted-foreground">{article.summary}</div>
                    </div>
                    <Badge className={`${classificationColor[article.classification]} text-xs`}>{classificationLabel[article.classification]}</Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-4">
                  <div className="pl-10 space-y-4">
                    <div>
                      <h4 className="font-medium text-foreground mb-2">Description</h4>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {article.description}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground mb-2">Reason</h4>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {article.reason}
                      </p>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </CardContent>
    </Card>
  );
}