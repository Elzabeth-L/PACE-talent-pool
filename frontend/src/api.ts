import type { CandidateDetail, CandidateList, Category, Proficiency, SkillRequirement } from "./types";

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal });
  if (!response.ok) throw new Error(response.status === 404 ? "The requested candidate was not found." : "The talent service is unavailable.");
  return response.json() as Promise<T>;
}

export const getCategories = () => request<Category[]>("/api/v1/categories");
export const getProficiencies = () => request<Proficiency[]>("/api/v1/proficiency-levels");
export const getCandidate = (id: string) => request<CandidateDetail>(`/api/v1/candidates/${id}`);

export function getCandidates(
  search: string,
  categoryId: number | null,
  requirements: SkillRequirement[],
  mode: "all" | "any",
  signal: AbortSignal,
) {
  const params = new URLSearchParams();
  if (search.trim()) params.set("q", search.trim());
  if (categoryId) params.set("category_id", String(categoryId));
  requirements.forEach((requirement) => params.append("skill", `${requirement.skill.skill_id}:${requirement.proficiencyRank ?? 1}`));
  params.set("match", mode);
  return request<CandidateList>(`/api/v1/candidates?${params}`, signal);
}
