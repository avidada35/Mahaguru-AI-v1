import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { BookOpen, Bookmark, Award, Clock, Search } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getDashboardStats } from '@/services/dashboard';
import { Skeleton } from '@/components/ui/skeleton';

const DashboardPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetch dashboard data
  const { data: stats, isLoading: isStatsLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: getDashboardStats,
  });

  // Simulate loading state
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading || isStatsLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="container py-8">
      <div className="flex flex-col space-y-8">
        {/* Welcome Section */}
        <div className="flex flex-col space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Welcome back, {stats?.userName || 'Learner'}!</h1>
          <p className="text-muted-foreground">
            Here's what's happening with your learning journey today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Active Courses"
            value={stats?.activeCourses || 0}
            icon={<BookOpen className="h-4 w-4 text-muted-foreground" />}
            description="Courses you're currently enrolled in"
          />
          <StatsCard
            title="Completed Lessons"
            value={stats?.completedLessons || 0}
            icon={<Bookmark className="h-4 w-4 text-muted-foreground" />}
            description="Lessons you've completed"
          />
          <StatsCard
            title="Learning Streak"
            value={`${stats?.streakDays || 0} days`}
            icon={<Award className="h-4 w-4 text-muted-foreground" />}
            description="Current learning streak"
          />
          <StatsCard
            title="Weekly Goal"
            value={`${stats?.weeklyGoalProgress || 0}%`}
            icon={<Clock className="h-4 w-4 text-muted-foreground" />}
            description="Weekly learning progress"
            progress={stats?.weeklyGoalProgress || 0}
          />
        </div>

        {/* Continue Learning */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-medium">Continue Learning</CardTitle>
            <Button variant="outline" size="sm">
              View All
            </Button>
          </CardHeader>
          <CardContent>
            {stats?.recentCourses && stats.recentCourses.length > 0 ? (
              <div className="space-y-4">
                {stats.recentCourses.map((course) => (
                  <div key={course.id} className="flex items-center p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="flex-1 space-y-1">
                      <p className="font-medium leading-none">{course.title}</p>
                      <p className="text-sm text-muted-foreground">{course.lastLesson}</p>
                      <Progress value={course.progress} className="h-2 mt-2" />
                    </div>
                    <Button size="sm" className="ml-4">
                      Continue
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 space-y-4">
                <Search className="h-12 w-12 mx-auto text-muted-foreground" />
                <h3 className="text-lg font-medium">No active courses</h3>
                <p className="text-sm text-muted-foreground">
                  Get started by exploring our courses
                </p>
                <Button className="mt-4">Browse Courses</Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.recentActivity && stats.recentActivity.length > 0 ? (
                  stats.recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-start pb-4 last:pb-0 last:border-0 border-b">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                        {activity.type === 'completed' ? (
                          <Bookmark className="h-5 w-5" />
                        ) : (
                          <BookOpen className="h-5 w-5" />
                        )}
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium">{activity.title}</p>
                        <p className="text-sm text-muted-foreground">{activity.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No recent activity to show
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Learning Goals */}
          <Card>
            <CardHeader>
              <CardTitle>Learning Goals</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {stats?.learningGoals && stats.learningGoals.length > 0 ? (
                  <>
                    {stats.learningGoals.map((goal) => (
                      <div key={goal.id} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium">{goal.title}</h4>
                          <span className="text-sm text-muted-foreground">
                            {goal.progress}%
                          </span>
                        </div>
                        <Progress value={goal.progress} className="h-2" />
                      </div>
                    ))}
                    <Button variant="outline" className="w-full mt-4">
                      Set New Goal
                    </Button>
                  </>
                ) : (
                  <div className="text-center py-8 space-y-4">
                    <Award className="h-12 w-12 mx-auto text-muted-foreground" />
                    <h3 className="text-lg font-medium">No learning goals set</h3>
                    <p className="text-sm text-muted-foreground">
                      Set learning goals to track your progress
                    </p>
                    <Button className="mt-4">Set Goals</Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

const StatsCard = ({
  title,
  value,
  icon,
  description,
  progress,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description: string;
  progress?: number;
}) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <div className="h-4 w-4 text-muted-foreground">{icon}</div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      <p className="text-xs text-muted-foreground">{description}</p>
      {progress !== undefined && (
        <Progress value={progress} className="h-2 mt-2" />
      )}
    </CardContent>
  </Card>
);

const DashboardSkeleton = () => (
  <div className="container py-8 space-y-8">
    <div className="space-y-2">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-96" />
    </div>

    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {[...Array(4)].map((_, i) => (
        <Card key={i}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-4 rounded-full" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-6 w-16" />
            <Skeleton className="h-3 w-32" />
          </CardContent>
        </Card>
      ))}
    </div>

    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="flex items-center p-4 space-x-4">
              <Skeleton className="h-12 w-12 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

export default DashboardPage;
