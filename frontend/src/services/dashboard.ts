import api from './api';

interface DashboardStats {
  userName: string;
  activeCourses: number;
  completedLessons: number;
  streakDays: number;
  weeklyGoalProgress: number;
  recentCourses: {
    id: string;
    title: string;
    lastLesson: string;
    progress: number;
  }[];
  recentActivity: {
    type: 'completed' | 'started';
    title: string;
    description: string;
    time: string;
  }[];
  learningGoals: {
    id: string;
    title: string;
    progress: number;
  }[];
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  // In a real app, this would be an API call
  // const response = await api.get('/dashboard/stats');
  // return response.data;

  // Mock data for now
  return {
    userName: 'Alex',
    activeCourses: 3,
    completedLessons: 24,
    streakDays: 7,
    weeklyGoalProgress: 75,
    recentCourses: [
      {
        id: '1',
        title: 'Introduction to Machine Learning',
        lastLesson: 'Neural Networks Basics',
        progress: 65,
      },
      {
        id: '2',
        title: 'Advanced React Patterns',
        lastLesson: 'Render Props in Depth',
        progress: 30,
      },
    ],
    recentActivity: [
      {
        type: 'completed',
        title: 'Completed lesson',
        description: 'Introduction to Neural Networks',
        time: '2 hours ago',
      },
      {
        type: 'started',
        title: 'Started new course',
        description: 'Advanced React Patterns',
        time: '1 day ago',
      },
      {
        type: 'completed',
        title: 'Completed quiz',
        description: 'Machine Learning Fundamentals',
        time: '2 days ago',
      },
    ],
    learningGoals: [
      {
        id: '1',
        title: 'Complete Machine Learning Course',
        progress: 65,
      },
      {
        id: '2',
        title: 'Spend 5 hours learning this week',
        progress: 75,
      },
    ],
  };
};
