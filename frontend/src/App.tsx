import { useEffect, useMemo, useState } from "react";
import { getCandidate, getCandidates, getCategories, getProficiencies } from "./api";
import type { Candidate, CandidateDetail, Category, Proficiency, SkillRequirement } from "./types";

function Logo() {
  return <div className="brand-mark" aria-hidden="true"><span>P</span></div>;
}

function SearchIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg>;
}

function CandidateRow({ candidate, onOpen }: { candidate: Candidate; onOpen: () => void }) {
  const initials = candidate.full_name.split(" ").map((part) => part[0]).join("").slice(0, 2);
  return (
    <button className="candidate-row" onClick={onOpen} aria-label={`Open ${candidate.full_name}'s profile`}>
      <span className="avatar">{initials}</span>
      <span className="candidate-identity">
        <strong>{candidate.full_name}</strong>
        <small>EMP {candidate.employee_id}</small>
      </span>
      <span className="candidate-email"><small>Corporate email</small><strong>{candidate.email}</strong></span>
      <span className="domain"><small>Capability focus</small><strong>{candidate.primary_category}</strong></span>
      {candidate.matched_skills.length > 0 && (
        <span className="matched-context">
          <small>Matches your skill filter</small>
          <span>{candidate.matched_skills.map((skill) => <b key={skill.skill_id}>{skill.skill_name}<em>{skill.proficiency_name}</em></b>)}</span>
        </span>
      )}
      <span className="profile-link">View profile <i>→</i></span>
    </button>
  );
}

function Directory({ onOpen }: { onOpen: (id: string) => void }) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [levels, setLevels] = useState<Proficiency[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [builderCategoryId, setBuilderCategoryId] = useState<number | null>(null);
  const [builderSkillId, setBuilderSkillId] = useState<number | null>(null);
  const [builderRank, setBuilderRank] = useState<number | null>(null);
  const [requirements, setRequirements] = useState<SkillRequirement[]>([]);
  const [mode, setMode] = useState<"all" | "any">("all");
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    Promise.all([getCategories(), getProficiencies()]).then(([categoryData, levelData]) => {
      setCategories(categoryData); setLevels(levelData);
    }).catch(() => setStatus("error"));
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setStatus("loading");
      getCandidates(search, categoryId, requirements, mode, controller.signal)
        .then((data) => { setCandidates(data.items); setTotal(data.total); setStatus("ready"); })
        .catch((error) => { if (error.name !== "AbortError") setStatus("error"); });
    }, 250);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [search, categoryId, requirements, mode]);

  const builderCategory = categories.find((category) => category.category_id === builderCategoryId);
  const selectedSkill = builderCategory?.skills.find((skill) => skill.skill_id === builderSkillId);
  const levelName = (rank: number | null) => rank === null ? "Any proficiency" : levels.find((level) => level.level_rank === rank)?.level_name ?? "Any proficiency";
  const addRequirement = () => {
    if (!builderCategory || !selectedSkill) return;
    setRequirements((current) => [...current.filter((item) => item.skill.skill_id !== selectedSkill.skill_id), {
      skill: selectedSkill, categoryName: builderCategory.category_name, proficiencyRank: builderRank,
    }]);
    setBuilderSkillId(null); setBuilderRank(null);
  };
  const clearAll = () => { setSearch(""); setCategoryId(null); setRequirements([]); setMode("all"); };
  const hasFilters = Boolean(search || categoryId || requirements.length);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><Logo/><div><strong>PACE</strong><small>Fresher Talent Pool</small></div></div>
        <label className="search"><SearchIcon/><span className="sr-only">Search candidates</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name or employee ID"/></label>
        <div className="header-note"><span>Talent intelligence</span><small>Built for better deployment decisions</small></div>
      </header>
      <main className="directory-layout">
        <aside className="filter-panel">
          <div className="filter-heading"><div><span className="eyebrow">DISCOVERY</span><h2>Find the right talent</h2></div>{hasFilters && <button className="text-button" onClick={clearAll}>Clear all</button>}</div>
          <label>Browse a capability area<select value={categoryId ?? ""} onChange={(event) => setCategoryId(event.target.value ? Number(event.target.value) : null)}><option value="">All capability areas</option>{categories.map((category) => <option value={category.category_id} key={category.category_id}>{category.category_name}</option>)}</select></label>
          <div className="divider" />
          <fieldset><legend>Add a skill filter</legend>
            <label>Capability area<select value={builderCategoryId ?? ""} onChange={(event) => { setBuilderCategoryId(event.target.value ? Number(event.target.value) : null); setBuilderSkillId(null); }}><option value="">Choose an area</option>{categories.map((category) => <option value={category.category_id} key={category.category_id}>{category.category_name}</option>)}</select></label>
            <label>Skill<select disabled={!builderCategory} value={builderSkillId ?? ""} onChange={(event) => setBuilderSkillId(event.target.value ? Number(event.target.value) : null)}><option value="">Choose a skill</option>{builderCategory?.skills.map((skill) => <option value={skill.skill_id} key={skill.skill_id}>{skill.skill_name}</option>)}</select></label>
            <label>Proficiency <span className="optional">Optional</span><select value={builderRank ?? ""} onChange={(event) => setBuilderRank(event.target.value ? Number(event.target.value) : null)}><option value="">Any proficiency</option>{levels.map((level) => <option value={level.level_rank} key={level.proficiency_id}>{level.level_name}</option>)}</select></label>
            <button className="primary-button" disabled={!selectedSkill} onClick={addRequirement}>Add skill filter</button>
          </fieldset>
          {requirements.length > 1 && <fieldset className="match-choice"><legend>Candidates should match</legend><label><input type="radio" checked={mode === "all"} onChange={() => setMode("all")}/><span><b>Every selected skill</b><small>Best for a specific skill combination</small></span></label><label><input type="radio" checked={mode === "any"} onChange={() => setMode("any")}/><span><b>At least one selected skill</b><small>Best for a broader talent search</small></span></label></fieldset>}
          <div className="filter-note"><strong>Tip</strong><p>Leave proficiency as “Any” to find everyone with exposure to that skill. Their actual level appears in the result row.</p></div>
        </aside>
        <section className="results-panel">
          <div className="results-header"><div><span className="eyebrow">TALENT DIRECTORY</span><h1>{status === "ready" ? total : "—"} candidate{total === 1 ? "" : "s"}</h1><p>Explore profiles across PACE’s fresher capability pool.</p></div><div className="results-mark"><b>{requirements.length}</b><span>active skill<br/>filter{requirements.length === 1 ? "" : "s"}</span></div></div>
          <div className="active-filters" aria-live="polite">
            {categoryId && <button onClick={() => setCategoryId(null)}>{categories.find((item) => item.category_id === categoryId)?.category_name} ×</button>}
            {requirements.map((requirement) => <button key={requirement.skill.skill_id} onClick={() => setRequirements((current) => current.filter((item) => item.skill.skill_id !== requirement.skill.skill_id))}>{requirement.skill.skill_name} · {levelName(requirement.proficiencyRank)} ×</button>)}
            {!categoryId && requirements.length === 0 && <span>Showing the complete talent pool</span>}
          </div>
          <div className="candidate-list">
            {status === "loading" && Array.from({length: 5}).map((_, index) => <div className="skeleton" key={index}/>) }
            {status === "error" && <div className="state"><b>We couldn’t load the talent pool.</b><span>Check the API connection and try again.</span></div>}
            {status === "ready" && candidates.length === 0 && <div className="state"><b>No candidates match this combination.</b><span>Try choosing Any proficiency or removing one skill filter.</span></div>}
            {status === "ready" && candidates.map((candidate) => <CandidateRow candidate={candidate} onOpen={() => onOpen(candidate.candidate_id)} key={candidate.candidate_id}/>) }
          </div>
        </section>
      </main>
    </div>
  );
}

function Profile({ id, onBack }: { id: string; onBack: () => void }) {
  const [candidate, setCandidate] = useState<CandidateDetail | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { getCandidate(id).then(setCandidate).catch((reason: Error) => setError(reason.message)); }, [id]);
  const categories = useMemo(() => candidate ? Object.entries(candidate.skills_by_category) : [], [candidate]);
  if (error) return <div className="profile-state"><b>{error}</b><button className="primary-button" onClick={onBack}>Return to Talent Pool</button></div>;
  if (!candidate) return <div className="profile-state"><div className="loader"/><span>Building talent profile…</span></div>;
  const initials = candidate.full_name.split(" ").map((part) => part[0]).join("").slice(0, 2);
  return (
    <div className="profile-shell">
      <header className="profile-topbar"><button className="back-button" onClick={onBack}>← <span>Talent Pool</span></button><div className="brand profile-brand"><Logo/><div><strong>PACE Talent Profile</strong><small>People · Abilities · Capability · Expertise</small></div></div><span className="employee-tag">EMP {candidate.employee_id}</span></header>
      <main className="profile-grid">
        <aside className="identity-card"><div className="profile-accent"/><div className="large-avatar">{initials}</div><span className="availability-dot">PACE FRESHER TALENT</span><h1>{candidate.full_name}</h1><a href={`mailto:${candidate.email}`}>{candidate.email}</a><div className="identity-stats"><div><small>Capability focus</small><strong>{candidate.primary_category}</strong></div><div><small>Skill groups</small><strong>{candidate.category_count}</strong></div><div><small>Assessed skills</small><strong>{candidate.skill_count}</strong></div><div><small>Highest level</small><strong>{candidate.top_proficiency}</strong></div></div><p className="profile-message">A concise view of demonstrated capability across the PACE fresher talent pool.</p></aside>
        <section className="competency-panel">
          <div className="profile-section-heading"><div><span className="eyebrow">CAPABILITY LANDSCAPE</span><h2>Skills & proficiency</h2><p>Every assessed skill appears once, grouped by capability area.</p></div><span>{candidate.skill_count} skills across {candidate.category_count} groups</span></div>
          <div className="competency-grid">{categories.map(([category, skills]) => <article className="competency-group" key={category}><h3>{category}<span>{skills.length}</span></h3><div>{skills.map((skill) => <div className="skill-line" key={skill.skill_id}><span>{skill.skill_name}</span><div className="bar" aria-label={`${skill.proficiency_name} proficiency`}><i style={{width: `${skill.proficiency_rank * 25}%`}}/></div><b>{skill.proficiency_name}</b></div>)}</div></article>)}</div>
        </section>
      </main>
    </div>
  );
}

export default function App() {
  const currentId = window.location.pathname.match(/^\/candidates\/([0-9a-f-]+)$/)?.[1] ?? null;
  const [candidateId, setCandidateId] = useState<string | null>(currentId);
  const navigate = (id: string | null) => { const path = id ? `/candidates/${id}` : "/"; window.history.pushState({}, "", path); setCandidateId(id); };
  useEffect(() => { const handler = () => setCandidateId(window.location.pathname.split("/")[2] || null); window.addEventListener("popstate", handler); return () => window.removeEventListener("popstate", handler); }, []);
  return candidateId ? <Profile id={candidateId} onBack={() => navigate(null)}/> : <Directory onOpen={(id) => navigate(id)}/>;
}
