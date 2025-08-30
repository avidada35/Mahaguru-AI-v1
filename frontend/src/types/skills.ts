export interface SkillRoadmap {
  id: string;
  title: string;
  description: string;
  milestones: Milestone[];
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  tutorials: Tutorial[];
  projects: Project[];
}

export interface Tutorial {
  id: string;
  title: string;
  description: string;
  url: string;
  completed: boolean;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  completed: boolean;
}
