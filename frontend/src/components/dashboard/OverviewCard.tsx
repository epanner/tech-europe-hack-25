import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface OverviewCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: "up" | "down" | "neutral";
  variant?: "default" | "danger" | "warning" | "success";
}

export function OverviewCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  variant = "default"
}: OverviewCardProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case "danger":
        return "border-danger/20 bg-gradient-danger";
      case "warning":
        return "border-warning/20 bg-gradient-to-br from-warning/10 to-warning/5";
      case "success":
        return "border-success/20 bg-gradient-success";
      default:
        return "border-border bg-gradient-security";
    }
  };

  const getIconColor = () => {
    switch (variant) {
      case "danger":
        return "text-danger";
      case "warning":
        return "text-warning";
      case "success":
        return "text-success";
      default:
        return "text-primary";
    }
  };

  return (
    <Card className={`${getVariantStyles()} shadow-card transition-all duration-300 hover:shadow-elevated hover:-translate-y-1 group relative`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-sm font-medium text-white/90 tracking-wide">
          {title}
        </CardTitle>
        <Icon className={`h-5 w-5 ${getIconColor()} transition-transform duration-300 group-hover:scale-110`} />
      </CardHeader>
      <CardContent className="pt-2">
        <div className="text-3xl font-bold text-white mb-2">{value}</div>
        {description && (
          <p className="text-sm text-white/80">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}