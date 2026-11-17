export interface Assessment {
  id: number;
  title: string;
  description: string;
  time_limit_minutes: number;
  question_count: number;
}

export interface Choice {
  id: number;
  text: string;
}

export interface Question {
  id: number;
  text: string;
  points: number;
  choices: Choice[];
}

export interface AssessmentDetail extends Assessment {
  questions: Question[];
}

export interface AttemptResult {
  message: string;
  score: number;
  total_points: number;
  earned_points: number;
  status: string;
}
