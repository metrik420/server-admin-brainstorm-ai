import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Server, 
  Network, 
  Database, 
  Shield, 
  Cloud, 
  Globe,
  Terminal,
  Mail,
  Layers,
  FileText
} from "lucide-react";

const topics = [
  { name: "Linux", icon: Terminal, count: 245, category: "System Admin", color: "bg-primary/20 text-primary" },
  { name: "Networking", icon: Network, count: 189, category: "Infrastructure", color: "bg-accent/20 text-accent" },
  { name: "MySQL", icon: Database, count: 156, category: "Database", color: "bg-primary/20 text-primary" },
  { name: "Apache", icon: Server, count: 134, category: "Web Server", color: "bg-accent/20 text-accent" },
  { name: "Security", icon: Shield, count: 167, category: "Security", color: "bg-destructive/20 text-destructive" },
  { name: "DNS", icon: Globe, count: 98, category: "Networking", color: "bg-accent/20 text-accent" },
  { name: "VMware", icon: Layers, count: 123, category: "Virtualization", color: "bg-primary/20 text-primary" },
  { name: "Cloud", icon: Cloud, count: 201, category: "Infrastructure", color: "bg-accent/20 text-accent" },
  { name: "Email", icon: Mail, count: 87, category: "Communication", color: "bg-primary/20 text-primary" },
];

export const TopicGrid = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-foreground">Knowledge Topics</h2>
        <Badge variant="outline" className="text-muted-foreground">
          {topics.reduce((sum, topic) => sum + topic.count, 0)} total articles
        </Badge>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {topics.map((topic) => (
          <Card 
            key={topic.name} 
            className="bg-gradient-card border-border shadow-card hover:shadow-glow transition-all duration-300 cursor-pointer group"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${topic.color}`}>
                    <topic.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <CardTitle className="text-lg group-hover:text-primary transition-colors">
                      {topic.name}
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">{topic.category}</p>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  {topic.count} articles
                </div>
                <div className="text-xs text-accent">
                  Last updated: 2h ago
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};