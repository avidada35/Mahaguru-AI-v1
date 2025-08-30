import api from './api';

export interface Lesson {
  id: string;
  title: string;
  content: string;
  completed: boolean;
  locked: boolean;
  duration: number; // in minutes
}

export interface Module {
  id: string;
  title: string;
  description: string;
  lessons: Lesson[];
  order: number;
}

export interface Question {
  id: string;
  text: string;
  answer?: string;
  askedBy: string;
  timestamp: string;
}

export interface Resource {
  id: string;
  title: string;
  type: 'document' | 'video' | 'link' | 'exercise';
  url: string;
  duration?: number; // in minutes, for videos
}

export interface ClassroomData {
  id: string;
  title: string;
  description: string;
  modules: Module[];
  currentLesson: {
    id: string;
    title: string;
    content: string;
  };
  previousLesson?: {
    id: string;
    title: string;
  };
  nextLesson?: {
    id: string;
    title: string;
  };
  questions: Question[];
  resources: Resource[];
  notes?: string;
}

export const getClassroomData = async (lessonId: string): Promise<ClassroomData> => {
  // In a real app, this would be an API call
  // const response = await api.get(`/classroom/${lessonId}`);
  // return response.data;

  // Mock data for now
  const mockModules: Module[] = [
    {
      id: 'module-1',
      title: 'Introduction to the Course',
      description: 'Get started with the basics',
      order: 1,
      lessons: [
        {
          id: 'lesson-1',
          title: 'Welcome to the Course',
          content: `# Welcome to the Course\n\nThis is the first lesson in the course. Here you'll learn the fundamentals.\n\n## What You'll Learn\n\n- Introduction to the subject\n- Course structure and expectations\n- How to succeed in this course\n\n## Getting Started\n\nLet's begin by understanding what this course is all about.`,
          completed: true,
          locked: false,
          duration: 15,
        },
        {
          id: 'lesson-2',
          title: 'Setting Up Your Environment',
          content: `# Setting Up Your Environment\n\nBefore we dive in, let's make sure you have everything you need.\n\n## Requirements\n\n- A computer with internet access\n- The latest version of the software\n- A code editor of your choice\n\n## Installation Steps\n\n1. Download and install the required software\n2. Configure your environment\n3. Verify the installation\n\n## Common Issues\n\nIf you encounter any issues, check our troubleshooting guide.`,
          completed: true,
          locked: false,
          duration: 20,
        },
      ],
    },
    {
      id: 'module-2',
      title: 'Core Concepts',
      description: 'Learn the fundamental concepts',
      order: 2,
      lessons: [
        {
          id: 'lesson-3',
          title: 'Understanding the Basics',
          content: `# Understanding the Basics\n\nIn this lesson, we'll cover the core concepts you need to know.\n\n## Key Concepts\n\n- Concept 1: Explanation\n- Concept 2: How it works\n- Concept 3: Real-world applications\n\n## Examples\n\nLet's look at some examples to better understand these concepts.`,
          completed: false,
          locked: false,
          duration: 30,
        },
        {
          id: 'lesson-4',
          title: 'Advanced Topics',
          content: `# Advanced Topics\n\nNow that we've covered the basics, let's dive deeper.\n\n## Advanced Concepts\n\n- Advanced concept 1\n- Advanced concept 2\n- Advanced concept 3\n\n## Practical Application\n\nLet's apply these concepts to solve real-world problems.`,
          completed: false,
          locked: true,
          duration: 45,
        },
      ],
    },
  ];

  // Find the current lesson
  const allLessons = mockModules.flatMap(module => module.lessons);
  const currentLesson = allLessons.find(lesson => lesson.id === lessonId) || allLessons[0];
  const currentIndex = allLessons.findIndex(lesson => lesson.id === currentLesson.id);
  
  const previousLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : undefined;
  const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : undefined;

  // Mock questions
  const questions: Question[] = [
    {
      id: 'q1',
      text: 'How do I install the required software on Windows?',
      answer: 'You can download the installer from our website and follow the installation wizard.',
      askedBy: 'John Doe',
      timestamp: '2 hours ago',
    },
    {
      id: 'q2',
      text: 'What are the prerequisites for this course?',
      answer: 'Basic programming knowledge is recommended but not required.',
      askedBy: 'Jane Smith',
      timestamp: '1 day ago',
    },
  ];

  // Mock resources
  const resources: Resource[] = [
    {
      id: 'r1',
      title: 'Course Syllabus',
      type: 'document',
      url: '#',
    },
    {
      id: 'r2',
      title: 'Introduction Video',
      type: 'video',
      url: '#',
      duration: 10,
    },
    {
      id: 'r3',
      title: 'Additional Reading Material',
      type: 'link',
      url: '#',
    },
  ];

  return {
    id: currentLesson.id,
    title: 'Introduction to the Course',
    description: 'Learn the fundamentals of the subject',
    modules: mockModules,
    currentLesson: {
      id: currentLesson.id,
      title: currentLesson.title,
      content: currentLesson.content,
    },
    previousLesson: previousLesson ? {
      id: previousLesson.id,
      title: previousLesson.title,
    } : undefined,
    nextLesson: nextLesson ? {
      id: nextLesson.id,
      title: nextLesson.title,
    } : undefined,
    questions,
    resources,
    notes: 'Remember to review the installation steps before the next lesson.',
  };
};
