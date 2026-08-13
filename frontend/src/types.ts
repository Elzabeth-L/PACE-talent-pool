export type Skill = { skill_id: number; category_id: number; skill_name: string };
export type Category = {
  category_id: number;
  category_name: string;
  display_order: number;
  skills: Skill[];
};
export type Proficiency = { proficiency_id: number; level_name: string; level_rank: number };
export type CandidateSkill = {
  skill_id: number;
  skill_name: string;
  category_id: number;
  category_name: string;
  proficiency_id: number;
  proficiency_name: string;
  proficiency_rank: number;
};
export type Candidate = {
  candidate_id: string;
  employee_id: string;
  full_name: string;
  email: string;
  primary_category: string;
  matched_skills: CandidateSkill[];
  skill_count: number;
};
export type CandidateDetail = Candidate & {
  top_proficiency: string;
  category_count: number;
  skills_by_category: Record<string, CandidateSkill[]>;
};
export type CandidateList = { items: Candidate[]; total: number; page: number; page_size: number };
export type SkillRequirement = { skill: Skill; categoryName: string; proficiencyRank: number | null };
