import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowLeft, 
  CheckCircle, 
  Lock, 
  PlayCircle, 
  BookOpen, 
  Award,
  ChevronDown,
  ChevronRight,
  Clock,
  BarChart2,
  Bookmark,
  Share2,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getSkillRoadmap } from '@/services/skills';

// Define types for our roadmap data
interface Tutorial {
  id: string;
  title: string;
  description: string;
  duration: number;
  type: 'video' | 'article' | 'interactive';
  url: string;
  completed: boolean;
  thumbnail?: string;
}

interface Project {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  completed: boolean;
}

interface Milestone {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  order: number;
  tutorials: Tutorial[];
  projects: Project[];
}

interface SkillRoadmap {
  id: string;
  title: string;
  description: string;
  icon: string;
  progress: number;
  hoursToComplete: number;
  prerequisites: string[];
  milestones: Milestone[];
  recommendedTutorials: Tutorial[];
}

export default function SkillRoadmapPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [expandedMilestones, setExpandedMilestones] = useState<Record<string, boolean>>({});
  const [activeTab, setActiveTab] = useState('roadmap');

  const { data: roadmap, isLoading, error } = useQuery({
    queryKey: ['skillRoadmap', id],
    queryFn: () => getSkillRoadmap(id || ''),
    enabled: !!id,
  });

  const toggleMilestone = (milestoneId: string) => {
    setExpandedMilestones(prev => ({
      ...prev,
      [milestoneId]: !prev[milestoneId]
    }));
  };

  const startLearning = (type: 'tutorial' | 'project', id: string) => {
    // In a real app, this would navigate to the learning content
    console.log(`Starting ${type}:`, id);
  };

  const handleBack = () => {
    navigate(-1);
  };

  if (isLoading) {
    return <LoadingState />;
  }

  if (error || !roadmap) {
    return <ErrorState onBack={handleBack} />;
  }

  return (
    <div className="container py-8">
      <Button variant="ghost" onClick={handleBack} className="mb-6">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Dashboard
      </Button>

      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{roadmap.title}</h1>
            <p className="text-muted-foreground mt-2 max-w-3xl">
              {roadmap.description}
            </p>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <Bookmark className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <StatCard 
            title="Progress" 
            value={`${roadmap.progress}%`}
            icon={<BarChart2 className="h-5 w-5" />}
          />
          <StatCard 
            title="Hours to Complete" 
            value={roadmap.hoursToComplete.toString()}
            icon={<Clock className="h-5 w-5" />}
          />
          <StatCard 
            title="Prerequisites" 
            value={roadmap.prerequisites.length.toString()}
            icon={<BookOpen className="h-5 w-5" />}
          />
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="roadmap">Learning Path</TabsTrigger>
          <TabsTrigger value="tutorials">Tutorials</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
        </TabsList>

        <TabsContent value="roadmap" className="space-y-6">
          {roadmap.milestones.map((milestone) => (
            <MilestoneCard
              key={milestone.id}
              milestone={milestone}
              isExpanded={!!expandedMilestones[milestone.id]}
              onToggle={() => toggleMilestone(milestone.id)}
              onStartLearning={startLearning}
            />
          ))}
        </TabsContent>

        <TabsContent value="tutorials">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {roadmap.recommendedTutorials.map((tutorial) => (
              <TutorialCard 
                key={tutorial.id} 
                tutorial={tutorial} 
                onStart={() => startLearning('tutorial', tutorial.id)} 
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="projects">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {roadmap.milestones.flatMap(milestone => 
              milestone.projects.map(project => (
                <ProjectCard 
                  key={project.id} 
                  project={project} 
                  onStart={() => startLearning('project', project.id)} 
                />
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Helper Components
function StatCard({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className="h-5 w-5 text-muted-foreground">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}

function MilestoneCard({ 
  milestone, 
  isExpanded, 
  onToggle,
  onStartLearning
}: { 
  milestone: Milestone;
  isExpanded: boolean;
  onToggle: () => void;
  onStartLearning: (type: 'tutorial' | 'project', id: string) => void;
}) {
  const completedTutorials = milestone.tutorials.filter(t => t.completed).length;
  const totalTutorials = milestone.tutorials.length;
  const progress = totalTutorials > 0 ? Math.round((completedTutorials / totalTutorials) * 100) : 0;

  return (
    <Card>
      <CardHeader 
        className="cursor-pointer hover:bg-accent/50 transition-colors rounded-t-lg"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center justify-center h-10 w-10 rounded-full ${
              milestone.completed ? 'bg-green-100 dark:bg-green-900' : 'bg-primary/10'
            }`}>
              {milestone.completed ? (
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              ) : (
                <span className="text-lg font-medium text-primary">
                  {milestone.order}
                </span>
              )}
            </div>
            <div>
              <CardTitle className="text-lg">{milestone.title}</CardTitle>
              <CardDescription className="mt-1">
                {milestone.description}
              </CardDescription>
            </div>
          </div>
          <Button variant="ghost" size="icon">
            {isExpanded ? (
              <ChevronDown className="h-5 w-5" />
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
          </Button>
        </div>
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="pt-0">
          <div className="mt-4 space-y-6">
            <div>
              <h4 className="font-medium mb-3">Tutorials ({completedTutorials}/{totalTutorials})</h4>
              <div className="space-y-2">
                {milestone.tutorials.map((tutorial) => (
                  <div 
                    key={tutorial.id}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-accent/50"
                  >
                    <div className="flex items-center space-x-3">
                      {tutorial.completed ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <PlayCircle className="h-5 w-5 text-muted-foreground" />
                      )}
                      <div>
                        <p className="font-medium">{tutorial.title}</p>
                        <p className="text-sm text-muted-foreground">
                          {tutorial.duration} min • {tutorial.type}
                        </p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onStartLearning('tutorial', tutorial.id);
                      }}
                    >
                      {tutorial.completed ? 'Review' : 'Start'}
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {milestone.projects.length > 0 && (
              <div>
                <h4 className="font-medium mb-3">Projects</h4>
                <div className="space-y-3">
                  {milestone.projects.map((project) => (
                    <div 
                      key={project.id}
                      className="p-4 border rounded-lg hover:border-primary/50 transition-colors"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium">{project.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            {project.description}
                          </p>
                          <div className="mt-2 flex items-center space-x-2">
                            <Badge variant="outline">
                              {project.difficulty}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {project.estimatedTime}
                            </span>
                          </div>
                        </div>
                        <Button 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onStartLearning('project', project.id);
                          }}
                        >
                          Start Project
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

function TutorialCard({ 
  tutorial, 
  onStart 
}: { 
  tutorial: Tutorial; 
  onStart: () => void;
}) {
  return (
    <Card className="h-full flex flex-col">
      <div className="aspect-video bg-muted flex items-center justify-center">
        {tutorial.thumbnail ? (
          <img 
            src={tutorial.thumbnail} 
            alt={tutorial.title} 
            className="w-full h-full object-cover"
          />
        ) : (
          <PlayCircle className="h-12 w-12 text-muted-foreground" />
        )}
      </div>
      <CardHeader>
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="mb-2">
            {tutorial.type}
          </Badge>
          <span className="text-sm text-muted-foreground flex items-center">
            <Clock className="h-3.5 w-3.5 mr-1" />
            {tutorial.duration} min
          </span>
        </div>
        <CardTitle className="text-lg">{tutorial.title}</CardTitle>
        <CardDescription className="line-clamp-2">
          {tutorial.description}
        </CardDescription>
      </CardHeader>
      <CardFooter className="mt-auto">
        <Button 
          variant={tutorial.completed ? "outline" : "default"} 
          className="w-full"
          onClick={onStart}
        >
          {tutorial.completed ? 'Review' : 'Start Learning'}
        </Button>
      </CardFooter>
    </Card>
  );
}

function ProjectCard({ 
  project, 
  onStart 
}: { 
  project: Project; 
  onStart: () => void;
}) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <Badge variant="outline">
            {project.difficulty}
          </Badge>
          <span className="text-sm text-muted-foreground flex items-center">
            <Clock className="h-3.5 w-3.5 mr-1" />
            {project.estimatedTime}
          </span>
        </div>
        <CardTitle className="text-lg">{project.title}</CardTitle>
        <CardDescription className="line-clamp-3">
          {project.description}
        </CardDescription>
      </CardHeader>
      <CardFooter className="mt-auto">
        <Button className="w-full" onClick={onStart}>
          Start Project
        </Button>
      </CardFooter>
    </Card>
  );
}

function LoadingState() {
  return (
    <div className="container py-8">
      <Skeleton className="h-10 w-48 mb-8" />
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-40" />
        ))}
      </div>
    </div>
  );
}

interface ErrorStateProps {
  onBack: () => void;
}

function ErrorState({ onBack }: ErrorStateProps) {
  return (
    <div className="container py-8">
      <Button variant="ghost" onClick={onBack} className="mb-6">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back
      </Button>
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-2">Roadmap Not Found</h2>
        <p className="text-muted-foreground mb-6">
          The requested skill roadmap could not be found or is not available.
        </p>
        <Button onClick={onBack}>Go Back</Button>
      </div>
    </div>
  );
}
