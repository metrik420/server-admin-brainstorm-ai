import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Play, Pause, Square, RefreshCw } from "lucide-react";
import { useState } from "react";

export const CrawlerStatus = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleStart = () => {
    setIsRunning(true);
    // Simulate progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsRunning(false);
          return 100;
        }
        return prev + 10;
      });
    }, 1000);
  };

  const handleStop = () => {
    setIsRunning(false);
    setProgress(0);
  };

  return (
    <Card className="bg-gradient-card border-border shadow-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Crawler Status</CardTitle>
          <Badge variant={isRunning ? "default" : "secondary"}>
            {isRunning ? "Running" : "Idle"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="text-foreground">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-muted-foreground">Sites Crawled:</span>
            <span className="ml-2 text-foreground font-medium">12/50</span>
          </div>
          <div>
            <span className="text-muted-foreground">Pages Found:</span>
            <span className="ml-2 text-foreground font-medium">1,234</span>
          </div>
          <div>
            <span className="text-muted-foreground">Processing:</span>
            <span className="ml-2 text-accent font-medium">linux-guides.com</span>
          </div>
          <div>
            <span className="text-muted-foreground">Last Update:</span>
            <span className="ml-2 text-foreground font-medium">2 min ago</span>
          </div>
        </div>

        <div className="flex space-x-2 pt-2">
          {!isRunning ? (
            <Button onClick={handleStart} size="sm" className="flex-1">
              <Play className="h-4 w-4 mr-2" />
              Start Crawl
            </Button>
          ) : (
            <Button onClick={handleStop} variant="destructive" size="sm" className="flex-1">
              <Square className="h-4 w-4 mr-2" />
              Stop
            </Button>
          )}
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};