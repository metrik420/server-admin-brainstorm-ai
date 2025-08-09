import { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

interface LogEvent {
  type: string;
  ts?: string;
  task_id?: string | null;
  [key: string]: any;
}

const formatTime = (iso?: string) => {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleTimeString();
  } catch {
    return iso;
  }
};

const levelColor = (type: string) => {
  if (type.includes("error") || type.includes("exception")) return "destructive" as const;
  if (type.includes("skip") || type.includes("disallow")) return "secondary" as const;
  if (type.includes("saved") || type.includes("complete")) return "default" as const;
  return "outline" as const;
};

export const LogsStream = () => {
  const [events, setEvents] = useState<LogEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const viewportRef = useRef<HTMLDivElement | null>(null);

  const wsUrl = useMemo(() => {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://${window.location.host}/api/logs/stream`;
  }, []);

  useEffect(() => {
    // prime with recent logs
    fetch("/api/logs/recent?n=200")
      .then((r) => r.json())
      .then((data) => setEvents(data.logs || []))
      .catch(() => {});

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (msg) => {
      try {
        const evt = JSON.parse(msg.data);
        setEvents((prev) => [...prev.slice(-499), evt]);
        // autoscroll
        requestAnimationFrame(() => {
          viewportRef.current?.scrollTo({ top: viewportRef.current.scrollHeight });
        });
      } catch {}
    };
    ws.onclose = () => {
      // try to reconnect after a delay
      setTimeout(() => {
        if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
          try {
            wsRef.current = new WebSocket(wsUrl);
          } catch {}
        }
      }, 3000);
    };

    return () => {
      ws.close();
    };
  }, [wsUrl]);

  return (
    <Card className="bg-gradient-card border-border shadow-card">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Crawler Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-72" viewportRef={viewportRef as any}>
          <div className="space-y-2 pr-2">
            {events.map((e, idx) => (
              <div key={idx} className="text-xs text-foreground flex items-start gap-2">
                <span className="text-muted-foreground min-w-[64px]">{formatTime(e.ts)}</span>
                <Badge variant={levelColor(e.type)}>{e.type}</Badge>
                <span className="break-words">
                  {e.url ? ` ${e.url}` : ""}
                  {e.topic ? ` [${e.topic}]` : ""}
                  {e.status ? ` status=${e.status}` : ""}
                  {e.value ? ` ${Math.round(e.value)}%` : ""}
                  {e.reason ? ` reason=${e.reason}` : ""}
                </span>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
