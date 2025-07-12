import { Header } from "@/components/Header";
import { StatsCard } from "@/components/StatsCard";
import { CrawlerStatus } from "@/components/CrawlerStatus";
import { TopicGrid } from "@/components/TopicGrid";
import { 
  FileText, 
  Database, 
  Activity, 
  Clock,
  TrendingUp 
} from "lucide-react";
import heroImage from "@/assets/hero-dashboard.jpg";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-background">
      <Header />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img 
            src={heroImage} 
            alt="Server Admin Dashboard" 
            className="w-full h-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-background/80" />
        </div>
        <div className="relative container mx-auto px-6 py-16">
          <div className="text-center space-y-6">
            <h1 className="text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              AI-Powered Server Admin Knowledge Engine
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Automatically crawl, organize, and enhance your technical knowledge. 
              Build the world's smartest assistant for server administration and troubleshooting.
            </p>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <section className="container mx-auto px-6 py-8 space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Articles"
            value="1,247"
            description="Knowledge base entries"
            icon={FileText}
            trend={{ value: "12%", isPositive: true }}
          />
          <StatsCard
            title="Active Crawlers"
            value="3"
            description="Currently processing"
            icon={Activity}
            trend={{ value: "2", isPositive: true }}
          />
          <StatsCard
            title="Topics Covered"
            value="18"
            description="Skill categories"
            icon={Database}
          />
          <StatsCard
            title="Last Update"
            value="2m ago"
            description="Content refresh"
            icon={Clock}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <TopicGrid />
          </div>
          <div className="space-y-6">
            <CrawlerStatus />
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
