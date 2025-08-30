// src/services/skills.ts
import { SkillRoadmap, Milestone, Tutorial, Project } from '../types/skills';

export const getSkillRoadmap = async (id: string): Promise<SkillRoadmap> => {
  // In a real app, this would be an API call
  // const response = await api.get(`/skills/roadmaps/${id}`);
  // return response.data;

  // Mock data
  return {
    id,
    title: "Full-Stack Web Development",
    description: "Master the skills needed to build modern web applications from frontend to backend.",
    icon: "💻",
    progress: 35,
    hoursToComplete: 120,
    prerequisites: [
      "Basic programming knowledge",
      "Understanding of HTML & CSS",
      "Basic JavaScript"
    ],
    milestones: [
      {
        id: "html-css",
        title: "HTML & CSS Fundamentals",
        description: "Learn the building blocks of the web",
        completed: true,
        order: 1,
        tutorials: [
          {
            id: "html-basics",
            title: "HTML5 Crash Course",
            description: "Learn the basics of HTML5",
            duration: 60,
            type: "video",
            url: "#",
            completed: true
          },
          {
            id: "css-basics",
            title: "CSS3 Fundamentals",
            description: "Master CSS3 and modern layout techniques",
            duration: 90,
            type: "video",
            url: "#",
            completed: true
          }
        ],
        projects: [
          {
            id: "portfolio-site",
            title: "Personal Portfolio",
            description: "Build a responsive portfolio website using HTML and CSS",
            difficulty: "beginner",
            estimatedTime: "4 hours",
            completed: true
          }
        ]
      },
      {
        id: "javascript",
        title: "JavaScript & DOM Manipulation",
        description: "Learn JavaScript and how to make web pages interactive",
        completed: false,
        order: 2,
        tutorials: [
          {
            id: "js-basics",
            title: "JavaScript Fundamentals",
            description: "Learn the core concepts of JavaScript",
            duration: 120,
            type: "video",
            url: "#",
            completed: true
          },
          {
            id: "dom-manipulation",
            title: "DOM Manipulation",
            description: "Learn to manipulate the DOM with JavaScript",
            duration: 90,
            type: "video",
            url: "#",
            completed: false
          }
        ],
        projects: [
          {
            id: "todo-app",
            title: "Todo List App",
            description: "Build a todo list application with JavaScript",
            difficulty: "beginner",
            estimatedTime: "6 hours",
            completed: false
          }
        ]
      },
      // Add more milestones as needed
    ],
    recommendedTutorials: [
      {
        id: "git-basics",
        title: "Git & GitHub for Beginners",
        description: "Learn version control with Git and GitHub",
        duration: 45,
        type: "video",
        url: "#",
        completed: false,
        thumbnail: "https://via.placeholder.com/300x200?text=Git+Tutorial"
      },
      {
        id: "responsive-design",
        title: "Responsive Web Design",
        description: "Make your websites look great on all devices",
        duration: 60,
        type: "article",
        url: "#",
        completed: false,
        thumbnail: "https://via.placeholder.com/300x200?text=Responsive+Design"
      }
    ]
  };
};