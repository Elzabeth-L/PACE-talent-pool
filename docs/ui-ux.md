# UI/UX specification

## Visual system

- Desktop-first, optimized for 1366×768 and above.
- Navy primary (`#12263f`), teal accent (`#087e8b`), warm off-white canvas.
- Inter/system sans typography, 4/8px spacing rhythm, restrained 8–12px radii.
- Proficiency uses labels plus bar length; color is never the sole signal.

## Talent Pool

```text
┌──────────────────────────────────────────────────────────────┐
│ PACE / Fresher Talent Pool      Search name or employee ID   │
├────────────────┬─────────────────────────────────────────────┤
│ FILTERS        │ 18 candidates                               │
│ Category       │ [AWS ≥ Advanced ×]             Clear all   │
│ Skill          ├─────────────────────────────────────────────┤
│ Minimum level  │ Candidate summary row                      │
│ Add requirement│ Candidate summary row                      │
│                │ Candidate summary row                      │
└────────────────┴─────────────────────────────────────────────┘
```

The left rail creates skill filters. Category selection limits the skill list. Proficiency is optional: “Any proficiency” means any assessed exposure. When multiple skills are selected, plain-language radio choices explain whether candidates must match every selected skill or at least one. Candidate rows do not display general skill lists; they show only identity and capability focus. While skill filters are active, the matching skills and actual proficiency appear as contextual evidence.

## PACE Talent Profile

```text
┌──────────────────────────────────────────────────────────────┐
│ ← Talent Pool   PACE Talent Profile               Employee ID│
├────────────────┬─────────────────────────────────────────────┤
│ Identity       │ Strongest skills                           │
│ Name           ├─────────────────────────────────────────────┤
│ Email          │ Competency groups in a compact matrix      │
│ Primary area   │ Category | skill label + proficiency bars  │
│                │                                             │
└────────────────┴─────────────────────────────────────────────┘
```

The page body and competency card do not scroll at 1366×768 for the approved prototype dataset. Every assessed skill appears exactly once in a two-column capability grid. Summary figures use aggregate information rather than repeating individual skills. No decorative charts are used.
