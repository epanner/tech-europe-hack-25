import { Button } from "@/components/ui/button";
import { Shield, Bell, Settings, User } from "lucide-react";

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-gradient-security shadow-card">
      <div className="container mx-auto px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <Shield className="h-9 w-9 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">DataGuard Pro</h1>
                <p className="text-sm text-muted-foreground tracking-wide">Data Protection Officer Dashboard</p>
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