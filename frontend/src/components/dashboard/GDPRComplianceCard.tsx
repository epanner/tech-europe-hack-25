import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { CheckCircle, AlertCircle, XCircle, FileText, ChevronDown } from "lucide-react";

interface GDPRArticle {
  article: string;
  title: string;
  status: "compliant" | "warning" | "violation";
  description: string;
  detailedAssessment: {
    requirements: string[];
    currentStatus: string;
    recommendations: string[];
    riskLevel: "low" | "medium" | "high";
    priority: "low" | "medium" | "high";
  };
}

const gdprArticles: GDPRArticle[] = [
  {
    article: "Art. 5",
    title: "Principles of Data Processing",
    status: "compliant",
    description: "Lawfulness, fairness, and transparency",
    detailedAssessment: {
      requirements: ["Data must be processed lawfully, fairly and transparently", "Data must be collected for specified, explicit and legitimate purposes", "Data must be adequate, relevant and limited"],
      currentStatus: "Your organization demonstrates good compliance with data processing principles. Privacy notices are clear and lawful bases are documented.",
      recommendations: ["Continue regular audits of data processing activities", "Ensure staff training on fair processing principles"],
      riskLevel: "low",
      priority: "low"
    }
  },
  {
    article: "Art. 6",
    title: "Lawfulness of Processing",
    status: "warning",
    description: "Legal basis for data processing",
    detailedAssessment: {
      requirements: ["Identify appropriate lawful basis before processing", "Document the lawful basis", "Inform individuals of the lawful basis", "Ensure lawful basis is appropriate for the purpose"],
      currentStatus: "Some data processing activities lack clearly documented lawful bases. Marketing consent mechanisms need review.",
      recommendations: ["Audit all processing activities and document lawful bases", "Review consent mechanisms", "Update privacy notices with specific lawful bases"],
      riskLevel: "medium",
      priority: "high"
    }
  },
  {
    article: "Art. 13",
    title: "Information to Data Subject",
    status: "compliant",
    description: "Transparency requirements",
    detailedAssessment: {
      requirements: ["Provide identity and contact details", "Provide purposes and lawful basis", "Provide information about recipients", "Provide retention periods", "Inform of data subject rights"],
      currentStatus: "Privacy notices contain required information and are easily accessible. Regular updates are maintained.",
      recommendations: ["Consider multi-layered privacy notices for complex processing", "Ensure privacy notices are available in relevant languages"],
      riskLevel: "low",
      priority: "low"
    }
  },
  {
    article: "Art. 17",
    title: "Right to Erasure",
    status: "violation",
    description: "Right to be forgotten",
    detailedAssessment: {
      requirements: ["Establish procedures for erasure requests", "Erase data without undue delay", "Inform third parties if data was disclosed", "Consider exemptions carefully"],
      currentStatus: "No formal erasure request process exists. Data retention schedules are unclear and some data is kept indefinitely.",
      recommendations: ["Implement formal erasure request procedures", "Create clear data retention schedules", "Train staff on right to erasure", "Audit data stores for unnecessary retention"],
      riskLevel: "high",
      priority: "high"
    }
  },
  {
    article: "Art. 25",
    title: "Data Protection by Design",
    status: "warning",
    description: "Privacy by design and default",
    detailedAssessment: {
      requirements: ["Implement appropriate technical measures", "Implement appropriate organisational measures", "Ensure data protection by default", "Consider data protection in system design"],
      currentStatus: "Some privacy-by-design principles are implemented but not consistently across all systems. New system development lacks formal privacy assessments.",
      recommendations: ["Implement mandatory privacy impact assessments for new systems", "Review existing systems for privacy-by-design compliance", "Establish privacy-by-default settings"],
      riskLevel: "medium",
      priority: "medium"
    }
  },
  {
    article: "Art. 32",
    title: "Security of Processing",
    status: "compliant",
    description: "Technical and organizational measures",
    detailedAssessment: {
      requirements: ["Implement appropriate security measures", "Consider encryption where appropriate", "Ensure ongoing confidentiality and integrity", "Regular testing and evaluation"],
      currentStatus: "Strong security controls are in place including encryption, access controls, and regular security assessments.",
      recommendations: ["Continue regular penetration testing", "Monitor for emerging security threats", "Review backup and recovery procedures"],
      riskLevel: "low",
      priority: "low"
    }
  },
  {
    article: "Art. 33",
    title: "Breach Notification",
    status: "warning",
    description: "Notification to supervisory authority",
    detailedAssessment: {
      requirements: ["Notify supervisory authority within 72 hours", "Document all personal data breaches", "Notify without undue delay", "Include required information in notification"],
      currentStatus: "Incident response procedures exist but notification timelines are unclear. Staff training on breach identification needs improvement.",
      recommendations: ["Clarify 72-hour notification procedures", "Improve staff training on incident identification", "Test incident response procedures regularly"],
      riskLevel: "medium",
      priority: "high"
    }
  },
  {
    article: "Art. 34",
    title: "Communication to Data Subject",
    status: "violation",
    description: "High-risk breach communication",
    detailedAssessment: {
      requirements: ["Communicate high-risk breaches to data subjects", "Communicate without undue delay", "Use clear and plain language", "Include specific required information"],
      currentStatus: "No formal process exists for communicating breaches to data subjects. Risk assessment procedures for determining communication requirements are missing.",
      recommendations: ["Develop breach communication procedures", "Create template communications for data subjects", "Establish risk assessment criteria", "Train communications team"],
      riskLevel: "high",
      priority: "high"
    }
  },
  {
    article: "Art. 35",
    title: "Data Protection Impact Assessment",
    status: "compliant",
    description: "DPIA requirements",
    detailedAssessment: {
      requirements: ["Conduct DPIA for high-risk processing", "Consult supervisory authority if necessary", "Review and update DPIAs regularly", "Consider data subject views"],
      currentStatus: "Comprehensive DPIA process is established and regularly used for high-risk processing activities.",
      recommendations: ["Regular review of DPIA thresholds", "Consider automation of DPIA workflows", "Ensure stakeholder engagement in DPIA process"],
      riskLevel: "low",
      priority: "low"
    }
  },
  {
    article: "Art. 44",
    title: "International Transfers",
    status: "warning",
    description: "Cross-border data transfers",
    detailedAssessment: {
      requirements: ["Ensure adequate level of protection", "Use appropriate safeguards", "Document transfer mechanisms", "Regular review of transfer arrangements"],
      currentStatus: "Some international transfers lack proper documentation of adequacy decisions or safeguards. Transfer inventory needs updating.",
      recommendations: ["Complete audit of all international transfers", "Implement Standard Contractual Clauses where needed", "Regular review of adequacy decisions", "Update transfer impact assessments"],
      riskLevel: "medium",
      priority: "medium"
    }
  }
];

export function GDPRComplianceCard() {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "compliant":
        return <CheckCircle className="h-4 w-4 text-success" />;
      case "warning":
        return <AlertCircle className="h-4 w-4 text-warning" />;
      case "violation":
        return <XCircle className="h-4 w-4 text-danger" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "compliant":
        return <Badge className="bg-success/20 text-success border-success/30">Compliant</Badge>;
      case "warning":
        return <Badge className="bg-warning/20 text-warning border-warning/30">Review Needed</Badge>;
      case "violation":
        return <Badge className="bg-danger/20 text-danger border-danger/30">Violation</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "text-danger";
      case "medium":
        return "text-warning";
      default:
        return "text-success";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "high":
        return "text-danger bg-danger/10";
      case "medium":
        return "text-warning bg-warning/10";
      default:
        return "text-success bg-success/10";
    }
  };

  const complianceStats = {
    compliant: gdprArticles.filter(a => a.status === "compliant").length,
    warning: gdprArticles.filter(a => a.status === "warning").length,
    violation: gdprArticles.filter(a => a.status === "violation").length
  };

  return (
    <Card className="bg-gradient-security border-border shadow-card hover:shadow-elevated transition-all duration-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-foreground">
          <FileText className="h-5 w-5 text-primary" />
          GDPR Compliance Assessment
        </CardTitle>
        <div className="flex gap-4 text-sm">
          <span className="text-success font-medium">✓ {complianceStats.compliant} Compliant</span>
          <span className="text-warning font-medium">⚠ {complianceStats.warning} Warnings</span>
          <span className="text-danger font-medium">✗ {complianceStats.violation} Violations</span>
        </div>
      </CardHeader>
      <CardContent>
        <Accordion type="multiple" className="space-y-2">
          {gdprArticles.map((article) => (
            <AccordionItem 
              key={article.article} 
              value={article.article}
              className="border border-border/50 rounded-lg px-3 data-[state=open]:shadow-inner-glow"
            >
              <AccordionTrigger className="hover:no-underline py-3">
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(article.status)}
                    <div className="text-left">
                      <div className="font-medium text-foreground">{article.article}: {article.title}</div>
                      <div className="text-sm text-muted-foreground">{article.description}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(article.status)}
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent className="pb-4">
                <div className="pl-10 space-y-4">
                  {/* Current Status */}
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Assessment Summary</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {article.detailedAssessment.currentStatus}
                    </p>
                  </div>

                  {/* Requirements */}
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Key Requirements</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {article.detailedAssessment.requirements.map((req, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span>{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Recommendations</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {article.detailedAssessment.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-primary mt-1">→</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Risk and Priority */}
                  <div className="flex gap-4 pt-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground">Risk Level:</span>
                      <Badge className={`${getRiskColor(article.detailedAssessment.riskLevel)} border-current/30 text-xs`}>
                        {article.detailedAssessment.riskLevel.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground">Priority:</span>
                      <Badge variant="outline" className={`${getPriorityColor(article.detailedAssessment.priority)} border-current/30 text-xs`}>
                        {article.detailedAssessment.priority.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}