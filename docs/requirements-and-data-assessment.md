# Requirements and Excel assessment

## Business objective

PACE Fresher Talent Pool lets managers answer “who has the skills I need?” quickly. The prototype is limited to talent discovery, relational filtering, and a Candidate 360° view. It does not include HR workflows, authentication, staffing automation, or project matching.

## Confirmed scope

- Search candidates by name and employee ID.
- Filter by category, skill, and minimum proficiency.
- Combine skill requirements using explicit ALL or ANY behavior.
- Display compact candidate summaries and a one-viewport profile.
- Use synthetic demonstration data only.
- Preserve the current candidate fields: employee ID, name, and email.
- Do not add education, location, availability, certifications, projects, training, or interest fields yet.

## Workbook assessment

The supplied workbook contains one worksheet, one response, and 96 columns: seven Forms/identity columns, fourteen category gate questions, and seventy-five skill/capability questions.

Candidate fields are Forms response ID, start/completion timestamps, email, name, last-modified timestamp, and employee ID. The sample employee ID was entered as an email address; imports normalize this to its numeric local part where valid (for example, `307373@ust.com` becomes `307373`).

The category Yes/No questions are intentional collection controls. A No answer skips that category’s proficiency questions. They remain part of import logic but are not stored as candidate profile attributes.

Observed proficiency values are Not used, Beginner, Working, Advanced, Expert, and Mastery. `ID` values in skipped sections are treated as invalid branching artifacts, never as proficiency.

## Data quality rules

- A category gate of No means its skill answers are ignored.
- Blank or `ID` answers mean not assessed.
- Not used is stored as explicit No Exposure.
- Employee IDs must contain digits only after normalization.
- The prototype seeds fictional candidates and does not import the supplied real response.
