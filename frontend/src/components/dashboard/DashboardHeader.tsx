import { Button } from "@/components/ui/button";
import { Bell, Settings, User } from "lucide-react";

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-gradient-security shadow-card">
      <div className="container mx-auto px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="Data Guard Pro Logo" className="h-20 w-400 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">Data Breach Assistant</h1>
                <p className="text-sm text-muted-foreground tracking-wide">Supporting in GDPR compliance assessments.</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}