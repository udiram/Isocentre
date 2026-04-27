from datetime import datetime, timezone

import markdown

from .models import Course, Page, RequirementRule, ResourceLink


OFFICIAL_LINKS = {
    "calendar": "https://academiccalendars.romcmaster.ca/preview_program.php?catoid=58&poid=29965&returnto=12628",
    "physics_programs": "https://physics.mcmaster.ca/undergraduate-studies/current-students/undergraduate-programs/",
    "physics_admissions": "https://physics.mcmaster.ca/undergraduate-studies/prospective-students/admissions-and-expectations/",
    "course_outlines": "https://physics.mcmaster.ca/undergraduate-studies/current-students/course-outlines/",
    "map": "https://mapsci.ca/level-2-programs/list/honours-medical-and-biological-physics/",
    "research_projects": "https://physics.mcmaster.ca/undergraduate-studies/current-students/upper-year-research-projects/",
    "radgrad_medphys": "https://radgrad.physics.mcmaster.ca/medical-physics/",
    "campep": "https://radgrad.physics.mcmaster.ca/programs/campep/",
    "mrsc": "https://sis.mcmaster.ca/undergraduate/medical-radiation-sciences/",
    "science_coop": "https://careers.science.mcmaster.ca/employers/co-op-programs/",
    "science_coop_prospective": "https://careers.science.mcmaster.ca/experience/prospective-students/",
    "science_coop_current": "https://careers.science.mcmaster.ca/experience/current-students/",
    "mrsc_faq": "https://sis.mcmaster.ca/undergraduate/medical-radiation-sciences/faq/",
    "nserc_usra": "https://nserc-crsng.canada.ca/en/funding-opportunity/undergraduate-student-research-awards",
    "mcmaster_usra": "https://research.mcmaster.ca/funding/undergraduate-student-research-award-usra/",
    "ccpm": "https://ccpm.ca/certification/",
    "campep_residency": "https://www.campep.org/ProspectiveApplicants.asp",
    "ontario_residency": "https://www.ontariohealth.ca/system/hhr/residency",
    "health_canada_rpb": "https://www.canada.ca/en/health-canada/corporate/about-health-canada/branches-agencies/healthy-environments-consumer-safety-branch/environmental-radiation-health-sciences-directorate/radiation-protection-bureau.html",
}


def md(text):
    return markdown.markdown(text or "", extensions=["extra", "smarty"])


PAGES = [
    {
        "slug": "medbiophys-explained",
        "title": "The honest guide to Medical & Biological Physics",
        "section": "Start Here",
        "summary": "What the program is, who it fits, and how to read official requirements without getting lost.",
        "is_featured": True,
        "source_confidence": "official-plus-student-advice",
        "source_links": [
            {"label": "2025-2026 Undergraduate Calendar", "url": OFFICIAL_LINKS["calendar"]},
            {"label": "Physics undergraduate programs", "url": OFFICIAL_LINKS["physics_programs"]},
            {"label": "MAP program page", "url": OFFICIAL_LINKS["map"]},
        ],
        "body_markdown": """
Medical & Biological Physics is a Physics & Astronomy degree pointed at living systems, medical imaging, radiation, soft matter, computation, and measurement. The official Physics page describes it as biologically relevant problems studied with physics techniques, including membranes, soft materials, molecular biophysics, computation, and laboratory methods. MAP adds medical imaging and processing, diagnostic and treatment tools, and transferable career skills.

## The core identity

This is not a clinical undergraduate program and it is not a lighter version of physics. It is a physics degree with enough biology, chemistry, anatomy, biochemistry, imaging, and radiation context to help you aim the physics toward health and life-science problems.

## What changes after first year

The official 2025-2026 calendar structure matters: newer students should not assume older course maps are still exact. PHYSICS 2B03 now appears in Level III requirements for students entering after September 2022, while Level II still contains Modern Physics, Introductory Lab, Scientific Computing, Differential Equations, a multivariable/vector calculus option, BIOPHYS 2S03, and biochemistry/anatomy-related requirements.

## The student-tested read

- If you like medical context but dislike math-heavy physics, this program will feel rough.
- If you like physics but want a route into imaging, radiation, biophysics, computation, health physics, or medical physics grad school, it can be a strong fit.
- If you want direct clinical training as a radiation therapist, radiographer, or sonographer, compare MRSc carefully.
- If you want medical school, plan GPA and prerequisites deliberately; this program is not designed as an easy GPA path.

## Use Isocentre correctly

Use official pages for policy. Use Isocentre for translation: workload warnings, pathway logic, course pairings, research strategy, co-op positioning, and student-reported survival advice.

## The program in one sentence

MedBioPhys is a physics-first degree for students who want to use measurement, modelling, computation, radiation, imaging, and biophysical thinking on biological or medical problems. That means the strongest students usually build three layers at the same time:

- Physics/math: mechanics, modern physics, E&M, differential equations, vector calculus, quantum, thermodynamics, mathematical physics.
- Biological/medical context: cell biology, chemistry, biochemistry, anatomy/physiology, radiation biology, imaging, clinical vocabulary.
- Evidence of doing: labs, code, research, co-op, thesis, posters, reports, or portfolios.

## What it is not

It is not direct clinical training. It does not make you a radiation therapist, radiographer, sonographer, or independent clinical medical physicist by itself. It also is not a "pre-med shortcut"; the program can prepare strong applicants for many routes, but the physics/math load can be unforgiving if GPA is the only goal.

## Who tends to thrive

- Students who like hard quantitative courses but want a reason beyond abstract physics.
- Students who can tolerate switching between derivations, code, wet/dry lab thinking, and biological memorization.
- Students who are willing to ask for advising early because the course calendar, MAP, co-op sequencing, and individual prerequisites do not always feel intuitive.
- Students who build a track: clinical medical physics, health physics, imaging/data, biophysics/soft matter, research/grad school, co-op/industry, or adjacent healthcare.

## First-year gateway strategy

Students can come from Life Sciences, Chemical & Physical Sciences, Math & Stats, Integrated Science, or other eligible Level I routes if they satisfy the official admission requirements. Life Sciences is common for students who want biology plus physics, but do not assume Life Sci automatically prepares you for the physics load. If you enter through a less physics-heavy route, use first year to protect calculus, physics, chemistry, and biology requirements aggressively.

## How to read official pages

MAP is useful for a quick overview and typical second-year courses. The Undergraduate Calendar is the binding requirement source. Department pages help with program identity, co-op, course outlines, and research opportunities. When they appear to differ, treat the calendar and academic advising as the decision layer.

## Best early moves

- Build a requirement tracker in first year instead of waiting for enrollment season.
- Take enough physics and math that Level II is not your first real physics year.
- Learn Python before you need it for a deadline.
- Go to office hours while the stakes are low.
- Start noticing which problems energize you: imaging, radiation, membranes, computation, clinical translation, instrumentation, or theory.
""",
    },
    {
        "slug": "medbiophys-vs-mrsc",
        "title": "MedBioPhys vs Medical Radiation Sciences",
        "section": "Comparisons",
        "summary": "The most common confusion: physics degree versus professional clinical radiation sciences program.",
        "is_featured": True,
        "source_links": [
            {"label": "Physics undergraduate programs", "url": OFFICIAL_LINKS["physics_programs"]},
            {"label": "Medical Radiation Sciences", "url": OFFICIAL_LINKS["mrsc"]},
            {"label": "MRSc FAQ", "url": OFFICIAL_LINKS["mrsc_faq"]},
        ],
        "body_markdown": """
These programs sound adjacent because both can touch radiation, imaging, anatomy, and healthcare. They are not interchangeable.

## MedBioPhys

Honours Medical & Biological Physics is housed in Physics & Astronomy. It builds physics, math, computation, labs, and biology/medical context. It can lead toward graduate school, medical physics, health physics, imaging research, biophysics, nuclear industry, scientific computing, and technical industry work.

## MRSc

Medical Radiation Sciences is a McMaster-Mohawk professional clinical undergraduate program. Official MRSc pages describe concurrent McMaster and Mohawk credentials and specializations in Radiography, Ultrasonography, and Radiation Therapy.

## Decision rule

- Want to become a radiation therapist, radiographer, or sonographer through a clinical undergraduate program? Investigate MRSc.
- Want a physics degree that can lead to medical physics graduate training, imaging/AI, radiation protection, biophysics, or technical research? Investigate MedBioPhys.
- Want clinical medical physics? MedBioPhys can be a strong start, but the path continues through graduate training, residency-style clinical training, and certification.

## Side-by-side

| Question | MedBioPhys | MRSc |
| --- | --- | --- |
| Academic home | Physics & Astronomy, Faculty of Science | School of Interdisciplinary Science with Mohawk College partnership |
| Main credential | Honours B.Sc. | McMaster Bachelor of Medical Radiation Sciences plus Mohawk advanced diploma |
| Main training style | Physics/math/computation/lab plus biological and medical context | Professional clinical education with academic and clinical components |
| Specializations | Student-built tracks: medical physics, health physics, imaging/data, biophysics, soft matter, industry | Radiography, Ultrasonography, Radiation Therapy beginning after Level I ranking/selection |
| Direct job identity | Technical/research/graduate-school preparation; not a licensed clinical role by itself | Front-line medical radiation and imaging professions, with certification/registration steps |
| Best fit | You want to understand and develop the physics, models, tools, and research behind medical/biological systems | You want structured clinical training to work directly as a technologist/therapist |

## Common confusion points

- Radiation therapist is not the same job as medical physicist. Radiation therapists deliver patient treatments; medical physicists commission, measure, model, verify, and improve the physics and safety of imaging/treatment systems.
- MRSc Radiation Therapy is a clinical undergraduate pathway. Clinical medical physics generally requires graduate medical physics training and clinical residency-style experience after undergrad.
- MedBioPhys can support imaging or radiation interests, but you must deliberately add research, coding, anatomy, radiation, and clinical-context evidence.
- MRSc includes clinical placements and professional competency alignment. MedBioPhys does not replace that.

## Which should a prospective student choose?

Choose MedBioPhys if you want optionality: graduate school, medical physics, health physics, biophysics, imaging AI, nuclear/radiation safety, software/data, or research. Choose MRSc if you already want one of the professional clinical radiation/imaging roles and prefer a highly structured clinical curriculum.
""",
    },
    {
        "slug": "level-ii-admission-guide",
        "title": "Level I to Level II admission guide",
        "section": "Roadmap",
        "summary": "Current official admission groups, first-year planning, and mistakes that create avoidable pain.",
        "is_featured": True,
        "source_links": [
            {"label": "2025-2026 Undergraduate Calendar", "url": OFFICIAL_LINKS["calendar"]},
            {"label": "MAP Honours Medical and Biological Physics", "url": OFFICIAL_LINKS["map"]},
        ],
        "body_markdown": """
The official 2025-2026 calendar lists admission from any Level I program with GPA at least 5.0 plus specific first-year course groups. The important practical point is that there are multiple acceptable routes, but you still need enough math and physics preparation to survive the program.

## Official admission buckets to track

- 6 units of first-year calculus/math from the approved math list.
- 3 units from the first physics mechanics/intro physics group.
- 3 units from MEDPHYS 1A03 or modern physics/waves-electricity alternatives.
- 3 units of chemistry from CHEM 1A03 or CHEM 1E03.
- 3 units from BIOLOGY 1A01/1A02/1A03, CHEM 1AA3, MATH 1B03, or MATH 1ZC3.
- 6 units from the Science I Course List.

## Strong recommendations in the calendar

The calendar notes that BIOLOGY 1A03, CHEM 1AA3, and MATH 1B03 are required by the end of Level II and strongly recommended in Level I. BIOLOGY 1M03 is recommended. MEDPHYS 1A03 and PHYSICS 1CC3 are also recommended in Level I.

## Mistakes to avoid

- Getting admitted but entering without enough physics confidence.
- Treating MEDPHYS 1A03 as a substitute for learning mechanics, waves, and fields.
- Missing CHEM 1AA3 or MATH 1B03 until it jams a Level II schedule.
- Assuming MAP's typical second-year list is the whole calendar requirement.

## Gateway-by-gateway planning

### Life Sciences I

This is common for students who like biology and physics. The risk is underestimating how physics-heavy MedBioPhys becomes. Protect both first-year physics courses where possible, take calculus seriously, and do not leave linear algebra/chemistry cleanup until Level II if you can avoid it.

### Chemical & Physical Sciences I

This route usually feels more natural for students already physics/chemistry oriented. The risk is not building enough biology/anatomy language early. Use electives and recommended courses to keep the biological side open.

### Math & Stats I

This can work well for students who want computation, imaging AI, modelling, or theory. The risk is missing biology/chemistry prerequisites or entering without enough experimental/lab context.

### Integrated Science

Integrated Science can connect well to interdisciplinary research, but students should confirm concentration and course requirements carefully because the structure is not identical to the standard Honours MedBioPhys path.

## First-year course planning logic

Use this order:

1. Satisfy admission buckets.
2. Add strongly recommended courses that become required or useful later.
3. Choose electives that preserve your likely track.
4. Avoid antirequisite traps and duplicated content.
5. Confirm with official advising if you are using an unusual route.

## What "competitive" means unofficially

The official minimum GPA is 5.0 and MAP describes the program as unlimited enrollment. That does not mean you should aim for the minimum. A stronger Level I gives you room to handle Level II, co-op applications, research outreach, and future graduate-school narratives. Treat anything above the minimum as academic breathing room, not just admission insurance.

## Level I winter checklist

- Run the Isocentre admission checker.
- Compare your plan against the Undergraduate Calendar, not only MAP.
- Confirm whether you still need BIOLOGY 1A03, CHEM 1AA3, MATH 1B03/MATH 1ZC3, MEDPHYS 1A03, or PHYSICS 1CC3/1AA3-type preparation.
- Build a draft Level II schedule and look for overload points.
- Ask one upper-year how the transition felt from your gateway.
""",
    },
    {
        "slug": "level-ii-survival-guide",
        "title": "Level II survival guide",
        "section": "Roadmap",
        "summary": "The practical guide to the physics shock year under the current calendar.",
        "is_featured": True,
        "source_links": [
            {"label": "2025-2026 Undergraduate Calendar", "url": OFFICIAL_LINKS["calendar"]},
            {"label": "MAP Honours Medical and Biological Physics", "url": OFFICIAL_LINKS["map"]},
            {"label": "Physics course outlines", "url": OFFICIAL_LINKS["course_outlines"]},
        ],
        "body_markdown": """
Level II is the year where MedBioPhys stops feeling like "Life Sci plus some physics" and starts feeling like a physics degree with biology, medicine, coding, and lab work attached. The official MAP page lists the typical second-year cluster students hear about: PHYSICS 2B03, 2C03, 2G03, 2P03, MATH 2C03, MATH 2X03, BIOPHYS 2S03, KINESIOL 2Y03, and BIOCHEM 2B03. The 2025-2026 calendar structure used by this site is more specific for current planning: PHYSICS 2B03 is positioned in Level III for newer entrants, while Level II still contains modern physics, lab, scientific computing, differential equations, multivariable/vector calculus, BIOPHYS 2S03, biochemistry, anatomy planning, and any first-year note courses you still owe.

Use this page as a survival system, not a substitute for advising. Always confirm your own calendar year, prerequisites, antirequisites, and term offerings.

## The Level II mission

By the end of Level II, you want four things:

- The official Level II requirement buckets protected.
- A working physics/math study system before PHYSICS 2B03, PHYSICS 3K03, MATH 3C03, and upper-year medical physics arrive.
- At least one concrete technical artifact: a Python notebook, lab report, mini-project, poster, or research email package.
- A better sense of whether your future is clinical medical physics, health physics, biophysics, imaging/data, co-op/industry, or another path.

## Official checklist, translated

| Requirement area | What it usually means | Student translation |
| --- | --- | --- |
| PHYSICS 2C03 and 2P03 | Modern Physics plus Introductory Laboratory | Theory plus reporting. Do not let lab reports become an afterthought. |
| Scientific computing | DATASCI 2G03 or PHYSICS 2G03 | Your coding backbone for imaging, simulation, data analysis, and research. |
| MATH 2C03 | Differential equations | The language of decay, oscillations, transport, circuits, population models, and many physics models. |
| Multivariable/vector calculus | MATH 2MC3, 2X03, or 2XA3 | The geometry you need before fields, gradients, divergence, curls, flux, and upper-year mathematical physics. |
| BIOPHYS 2S03 | Explorations in Medical and Biological Physics | Your first "why this program exists" course: physics methods applied to living/medical systems. |
| Biochemistry option | One course from the approved biochemistry group | Pick with your future in mind: molecular biophysics, clinical background, or life-science breadth. |
| Admission-note cleanup | BIOLOGY 1A03, CHEM 1AA3, MATH 1B03/MATH 1ZC3 if not done | Do not leave these vague. They can quietly constrain Level III/IV planning. |
| Anatomy/physiology | KINESIOL 2X03 or 2Y03 required by graduation | Helpful earlier if clinical medical physics, imaging, MR anatomy, or radiation therapy interests you. |

## A realistic term-by-term rhythm

There is no universal perfect schedule because offerings, co-op, electives, and your first-year background matter. But the logic should look like this:

### Before September

- Review first-year mechanics, waves/modern physics, calculus, and linear algebra basics.
- Install and test your Python environment before scientific computing starts.
- Make a one-page requirement tracker from the calendar and Isocentre planner.
- Decide which course will be your "deep work anchor" each term. Usually this is math, computing, or lab.
- If you are aiming for research, clean up your resume and make a small GitHub/notebook/project folder.

### Fall term

- Treat the first three weeks as setup, not shopping period drift.
- For modern physics, build a formula/concept map after every lecture.
- For lab, write methods and analysis notes the same day data is collected.
- For math, do enough problems that you know which step fails: setup, algebra, calculus, or interpretation.
- If co-op is on the table, start translating your program into resume language now.

### Winter term

- Use January to identify summer research and NSERC USRA possibilities.
- Start targeted professor emails in January/February if you have a plausible fit.
- Use computing/lab outputs as evidence in research emails instead of just saying you are interested.
- Run the program planner before enrollment decisions for Level III.
- Ask upper-years what each Course List A/B/C choice actually felt like before you commit.

### Spring and summer after Level II

- Best case: paid research, NSERC USRA, co-op preparation, hospital/lab/data work, or a supervisor-backed project.
- Good backup: self-directed imaging, simulation, radiation, or biophysics project with a public writeup.
- Minimum useful output: one clean technical artifact and one paragraph explaining what you learned.

## Course-by-course survival notes

### PHYSICS 2C03 - Modern Physics

This course is usually the conceptual bridge between first-year physics and upper-year quantum, radiation, and imaging ideas. Expect model changes: particles behave like waves, energy levels become discrete, and intuition from everyday mechanics becomes less reliable.

What to review:

- Waves, interference, energy, momentum, basic probability, and first-year modern physics if you took it.
- Exponential decay and logarithms; these appear everywhere later in radiation and medical physics.
- Basic linear algebra language: vectors, basis states, eigenvalue intuition, and complex numbers if covered.

What makes it hard:

- Students memorize equations without knowing the assumptions.
- Unit conversions and constants quietly cause wrong answers.
- Conceptual questions punish "plug and chug" studying.

How to study:

- For every equation, write: when can I use it, what does each symbol mean, and what would make it invalid?
- Redo derivations until you can explain the physical idea in plain English.
- Keep a one-page "modern physics dictionary" for terms like quantization, uncertainty, tunnelling, wavefunction, decay constant, and cross section.

What it unlocks:

- Quantum mechanics, radiation physics, nuclear/particle ideas, medical imaging physics, and clinical medical physics vocabulary.

### PHYSICS 2P03 - Introductory Laboratory

This is not just "labs." It is where you learn whether your measurements, plots, uncertainty, and writing can survive scrutiny. It matters for research because professors care about students who can keep records and interpret messy data.

What to review:

- Uncertainty propagation, linear fits, residuals, significant figures, graph captions, and basic instrument notes.
- How to write a methods section that someone else could repeat.

What makes it hard:

- Reports take longer than expected because data analysis reveals problems late.
- Students record too little detail during the lab and cannot defend choices later.
- Figures look pretty but do not answer the experimental question.

How to study/work:

- Start the report template before the lab if the experiment is known.
- During the lab, write down settings, uncertainties, failed attempts, and weird observations.
- Build plots early and check residuals, not just R-squared.
- Finish the analysis before polishing prose.

What it unlocks:

- Thesis readiness, summer research credibility, instrumentation roles, health physics measurement work, and better scientific communication.

### PHYSICS 2G03 or DATASCI 2G03 - Scientific Computing

This is the highest-leverage Level II course if you want imaging, AI, simulation, co-op, or research. The point is not just syntax. The point is turning physical questions into reproducible computations.

What to review:

- Python basics, arrays, loops, functions, plotting, file paths, and debugging.
- Algebra and units, because code with wrong physics is still wrong.

What makes it hard:

- Leaving assignments until the end because "it is just coding."
- Copying notebook patterns without understanding data shapes.
- Generating plots without interpreting them physically.

How to study:

- Start every assignment the day it is released, even if only to load data and run starter code.
- Use tiny test cases before full simulations.
- Comment the physics logic, not every line of code.
- Save clean notebooks as portfolio artifacts after grading.

What it unlocks:

- Medical imaging analysis, MRI/CT/PET data work, radiotherapy data, computational biophysics, co-op roles, and thesis projects.

### MATH 2C03 - Differential Equations

Differential equations are how physics describes change. This course pays off later in decay, diffusion, oscillations, circuits, transport, pharmacokinetics-style models, and many biological systems.

What to review:

- Integration techniques, derivatives, complex exponentials, trig identities, and first-order linear equations.
- Interpreting constants and initial conditions physically.

What makes it hard:

- Students learn solution recipes but cannot identify the equation type.
- Algebra mistakes hide conceptual mistakes.
- Word problems require translating a system into an equation before solving.

How to study:

- Make a decision tree: separable, linear first-order, second-order constant coefficients, systems, Laplace, series, or numerical.
- After solving, sketch the behavior and ask whether it makes physical sense.
- Redo examples without looking at the first line of the solution.

What it unlocks:

- E&M, statistical mechanics, mathematical physics, modelling life, radiation decay, diffusion, and computational projects.

### MATH 2X03 / 2MC3 / 2XA3 - Multivariable and vector calculus

This is the math students underestimate. It becomes the grammar for fields, gradients, flux, optimization, volumes, and coordinate systems.

What to review:

- Vectors, dot/cross products, partial derivatives, integrals, parametric curves/surfaces, and coordinate systems.
- Linear algebra basics if you are also cleaning up MATH 1B03.

What makes it hard:

- Geometry is the real problem, not just calculus.
- Bad coordinate choices make otherwise reasonable problems painful.
- Students skip diagrams and lose the physical meaning of the integral.

How to study:

- Draw the region, field, or surface before writing integrals.
- Keep a "coordinate systems" page with when Cartesian, cylindrical, or spherical makes sense.
- Explain each integral boundary in words.

What it unlocks:

- PHYSICS 2B03, MATH 3C03, electromagnetism, imaging fields, fluid/soft matter ideas, and advanced physics modelling.

### BIOPHYS 2S03 - Explorations in Medical and Biological Physics

This is the program identity course. Use it to sample what kind of MedBioPhys student you are becoming: imaging, membranes, molecular biophysics, radiation, computation, instrumentation, or biological modelling.

What to review:

- Basic biology vocabulary, diffusion, forces/energy, statistics, and graph interpretation.
- The ability to explain physics to a biology audience and biology to a physics audience.

What makes it hard:

- Treating each topic as disconnected.
- Remembering biological details without asking what measurement or model is being used.
- Not using it to discover research interests.

How to study:

- For each unit, write two sentences: the biological question and the physics method.
- Track which topics make you curious enough to read a paper.
- Use assignments or presentations as future research-email talking points.

What it unlocks:

- Faculty fit, thesis direction, Course List choices, and the difference between "medical physics" and broader biological physics.

### BIOCHEM option - 2B03, 2BB3, 2EE3, or 3G03 depending on your path

The biochemistry requirement is not just a box. It shapes whether you can speak seriously about molecular systems, proteins, metabolism, nucleic acids, or biological mechanisms.

How to choose:

- Molecular biophysics or wet-lab-adjacent research: choose the option that gives stronger protein/nucleic-acid/mechanism background.
- Clinical medical physics: choose a course that keeps you competent with cell biology, radiation biology later, and biomedical language.
- Imaging/data: choose the course you can handle while keeping coding/math strong.

Survival tip:

- Use spaced repetition from week one. Physics students often underestimate how much terminology and pathway detail these courses require.

### KINESIOL 2X03 / 2Y03 - Human Anatomy and Physiology I

This is required by graduation and often useful before clinical medical physics, imaging, radiation therapy context, or MRI/CT anatomy discussions.

What makes it hard:

- High memorization density.
- Exams may reward fast recall and detail recognition more than derivation-style thinking.
- It competes directly with physics/math time if scheduled carelessly.

How to study:

- Use active recall and diagrams.
- Pair anatomy structures with imaging relevance when possible.
- Do not put off memorization until the week before tests.

## Common failure patterns

- Treating every course the same. Physics, math, lab, coding, and biology reward different study behaviors.
- Letting lab reports and coding assignments become weekend emergencies.
- Choosing electives by vibes instead of future track.
- Ignoring office hours until after the first midterm goes badly.
- Forgetting that Level II is also when research/co-op positioning starts.
- Not checking prerequisites, antirequisites, and calendar-year rules.

## The weekly operating system

Use a weekly reset, preferably Friday afternoon or Sunday morning:

1. List every due date for the next 14 days.
2. Pick the one assignment that can explode if started late: usually coding or lab.
3. Block two math/physics problem sessions before office hours/tutorials.
4. Add one biology/anatomy/biochem recall session every 1-2 days.
5. Write one sentence about what each course is currently teaching you that could matter later.
6. Move one career/research task forward: resume bullet, professor shortlist, course review, mentor message, or project note.

## Midterm and exam strategy

- Modern physics: mix conceptual questions with derivations and calculation drills.
- Lab: your "exam" is often cumulative habits; keep analysis and uncertainty clean all term.
- Computing: build a debugging checklist and know how to explain your outputs.
- Differential equations: identify equation types quickly, then solve.
- Vector calculus: draw geometry first, then integrate.
- Biochem/anatomy: active recall beats rereading.

## Research and NSERC timing

Level II winter is the first serious window for summer research. For NSERC USRA or paid RA work, do not start with the form. Start with supervisor fit.

Strong outreach package:

- A one-page resume.
- A short unofficial transcript if requested.
- A concrete reason for contacting that professor.
- Evidence from Level II: coding notebook, lab report, BIOPHYS 2S03 topic, imaging interest, radiation interest, or math/physics preparation.
- A clear ask: summer research, NSERC USRA support, volunteer project, thesis-track conversation, or advice on becoming competitive.

Email in January or February if you can. One tailored message to a good-fit professor is better than ten vague messages.

## Co-op timing

If you are considering co-op, Level II is when your resume must become legible to employers. "Medical and Biological Physics" will not explain itself. Translate it into:

- Physics/math problem solving.
- Python/data/scientific computing.
- Lab measurement and uncertainty.
- Biology/anatomy/medical context.
- Communication across technical and clinical/science audiences.

## If the year is going badly

Do not wait for a perfect reset. Triage.

- First, protect required courses and prerequisites.
- Second, identify the course with the most recoverable marks left.
- Third, go to office hours with a specific failed attempt, not "I do not understand anything."
- Fourth, reduce optional commitments until the core is stable.
- Fifth, talk to academic advising if requirements, withdrawals, overload, or sequencing are in question.

## What good looks like by April

You do not need a perfect transcript to have had a strong Level II. A strong finish looks like this:

- You know which official requirements are complete and which remain.
- You can write, debug, plot, and explain a small scientific computing task.
- You can write a defensible lab report with uncertainty and clear figures.
- You can name 2-4 faculty or research areas that actually fit you.
- You have a realistic Level III plan, including PHYSICS 2B03 if it is still ahead.
- You understand whether your next move is research, co-op, clinical medical physics preparation, health physics, biophysics, imaging/data, or another route.
""",
    },
    {
        "slug": "upper-year-planning",
        "title": "Level III/IV: choose your identity",
        "section": "Roadmap",
        "summary": "How to turn Course Lists A/B/C into a coherent future instead of random electives.",
        "is_featured": True,
        "source_links": [{"label": "2025-2026 Undergraduate Calendar", "url": OFFICIAL_LINKS["calendar"]}],
        "body_markdown": """
The official program notes say students may mix Course List A, B, and C, but they also recommend 12 units from a focus list if you are aiming at that area. That is the difference between a random transcript and a credible story.

## Course List A: Medical Physics / Health Physics

Use this for clinical medical physics, health physics, radiation protection, imaging, nuclear medicine, radiation biology, or CAMPEP-facing preparation. Prioritize MEDPHYS 4B03, 4D03, 4F03, 4U03, MEDPHYS 4RA3/4RB3, PHYSICS 4E03, and a senior project if possible.

## Course List B: Biological Physics / Biochemistry

Use this for molecular biophysics, wet-lab-adjacent research, biochemical mechanisms, genomics, biotechnology, pharmacology, membranes, or life-science graduate work.

## Course List C: Soft Matter / Physics

Use this for soft condensed matter, computational physics, optics, advanced lab, quantum, instrumentation, theory, and physics-forward graduate school.

## Student-tested rule

Pick one primary identity and one secondary skill. Examples: medical physics + coding, biophysics + wet lab, soft matter + computation, health physics + communication.

## Required core, student translation

The upper-year core is where the program becomes coherent. PHYSICS 2B03 gives the field theory background students expect from physics. PHYSICS 3K03 connects thermal/statistical reasoning to soft matter and biological systems. MATH 3C03 strengthens mathematical physics. BIOPHYS 3S03 and BIOPHYS 4S03 connect soft matter and molecular biophysics to the medical/biological identity. MEDPHYS 4B03, 4RA3, and 4T03 are major anchors for radiation and clinical medical physics.

## How to choose electives without wasting them

Ask four questions before adding an elective:

- Does this satisfy an official requirement or focus-list recommendation?
- Does it build a prerequisite for a future course, thesis, co-op, or grad school?
- Can I explain why it belongs in my story?
- Does the workload fit the rest of the term?

## Course List A: medical physics / health physics

Prioritize this if you want clinical medical physics, radiation therapy physics, imaging, health physics, nuclear medicine, radiation biology, dosimetry, or radiation safety. Strong combinations include:

- MEDPHYS 4B03 plus MEDPHYS 4RA3/4RB3 for radiation and radioisotope methodology.
- MEDPHYS 4D03 for imaging and signal formation.
- MEDPHYS 4F03 or MEDPHYS 3C03 for health physics and radiation protection.
- MEDPHYS 4U03 for radiation biology.
- MEDPHYS 4Y06 or PHYSICS 4P06 if you can turn interest into a serious project.

## Course List B: biological physics / biochemistry

Prioritize this if you want molecular biophysics, biotechnology, wet-lab-adjacent research, proteins, membranes, pharmacology, genomics, or biological mechanisms. This path pairs well with BIOPHYS 4S03, BIOCHEM electives, BIOPHYS 3G03, and a project with a molecular/biophysical lab.

## Course List C: soft matter / physics

Prioritize this if you want soft condensed matter, advanced physics, optics, computational physics, experimental physics, or physics-forward graduate work. This path pairs well with BIOPHYS 3S03, PHYSICS 3P03, PHYSICS 4G03, PHYSICS 4K03, and senior project work.

## Thesis and senior project decision

Do a thesis/project if you need evidence for grad school, research jobs, medical physics applications, or a strong faculty reference. Do not choose a project only by title. Choose by supervision fit, weekly work style, technical skills, and final deliverables.

## Upper-year term planning

- Level III fall/winter: protect PHYSICS 2B03, PHYSICS 3K03, MATH 3C03, BIOPHYS 3S03, and track-defining electives.
- Summer after Level III: research, co-op, NSERC/USRA-style work, hospital/data/radiation safety exposure, or a portfolio project.
- Level IV fall: thesis/project launch, graduate applications, references, and remaining core.
- Level IV winter: finish with proof: report, poster, code, figures, presentation, and a clear next-step story.
""",
    },
    {
        "slug": "research-guide",
        "title": "Research, thesis, and supervisor guide",
        "section": "Research",
        "summary": "How to get research earlier and use upper-year projects strategically.",
        "is_featured": True,
        "source_links": [
            {"label": "Upper-year research projects", "url": OFFICIAL_LINKS["research_projects"]},
            {"label": "McMaster USRA", "url": OFFICIAL_LINKS["mcmaster_usra"]},
            {"label": "NSERC USRA", "url": OFFICIAL_LINKS["nserc_usra"]},
        ],
        "body_markdown": """
McMaster Physics describes upper-year projects as research projects, literature reviews, teaching placements, and independent study. The senior research project includes research, a poster, an oral presentation, and a written report. For 2025-2026 and 2026-2027, the official page also lists coordinators and notes that outside-department supervisors need approval.

## How to get research in second year

Start with fit, not prestige. Make a shortlist by method: coding-heavy, imaging, radiation, wet lab, soft matter, instrumentation, computation, or theory. Email with one specific reason for fit and one concrete skill you can bring.

## Supervisor matching

Good fit means the project matches your actual weekly tolerance. Wet lab means protocols and repetition. Imaging/AI means code, data cleaning, and validation. Radiation/health physics means safety culture and careful measurement. Soft matter means physical intuition plus math or experimental technique.

## Senior project strategy

If you are considering grad school, clinical medical physics, or research-heavy industry, a senior project can become your strongest evidence: poster, talk, writing sample, reference letter, and interview story.

## Research routes by year

### Level I

Your job is exploration. Go to talks, learn faculty names, ask TAs what their labs do, and build basic skills. A cold email can work, but most students are stronger if they first develop one small artifact: a code notebook, literature summary, lab technique, or strong course performance.

### Level II

This is the first serious window. BIOPHYS 2S03, PHYSICS/DATASCI 2G03, PHYSICS 2P03, and modern physics give you something to talk about. In January/February, contact a small number of targeted faculty for summer research or NSERC USRA possibilities.

### Level III

Start thesis/senior project conversations before final year. Bring a short resume, transcript, course list, technical skills, and a clear reason for fit. If you wait until enrollment season, good projects may already be informally filled.

### Level IV

Turn your project into proof: poster, oral presentation, report, code repository, abstract, figure set, or reference letter. A good project is not just "I worked in a lab"; it is evidence that you can define a problem, work through ambiguity, and communicate results.

## NSERC USRA strategy

NSERC USRA is one of the cleanest ways to get paid undergraduate research if you are eligible and a supervisor supports the application. McMaster’s USRA page handles institutional process details, while NSERC sets national eligibility and application requirements.

What makes a strong USRA application:

- Supervisor fit: your proposed work clearly matches the professor’s research.
- Evidence: transcript plus specific skills from computing, lab, physics, biochemistry, imaging, radiation, writing, or modelling.
- Specificity: "I want to learn MRI image processing" is stronger than "I am interested in medical physics."
- Timing: begin conversations early enough for departmental deadlines.
- Backup plan: if USRA is not possible, ask about SURA, paid RA, volunteer, thesis-track, or reading-project options.

## How to choose a professor

Pick by method and environment, not just topic name:

- Clinical/radiation: dosimetry, imaging, treatment planning, QA, radiation safety.
- Imaging/data: MRI, CT, PET/SPECT, segmentation, reconstruction, image quality, Python/MATLAB.
- Molecular biophysics: microscopy, membranes, proteins, condensates, diffusion, single-molecule methods.
- Soft matter: polymers, vesicles, colloids, interfaces, rheology, scattering, simulation.
- Computation/theory: modelling, simulations, origin of life, statistical mechanics, mathematical physics.

## Outreach template

Subject: Undergraduate research inquiry - [specific method/topic]

Dear Professor [Name],

I am a Level [II/III/IV] Medical & Biological Physics student interested in [specific area]. I saw that your group works on [specific project/method], and I am especially interested in [concrete reason].

My relevant background is [2-3 courses/skills/artifacts]. I am looking for [summer research / NSERC USRA / thesis supervision / volunteer research] and wondered whether there may be a fit.

I attached my resume and transcript. If you are not taking students, I would appreciate any advice on what would make me a stronger applicant later.

Best, [Name]

## What to ask in a first meeting

- What would the first four weeks of the project look like?
- What skills should I learn before starting?
- How often do undergrads meet with the supervisor or graduate mentor?
- What are realistic outputs: poster, report, code, figures, manuscript contribution?
- Is the project better suited for summer, thesis, reading course, or volunteer work?
""",
    },
    {
        "slug": "coop-guide",
        "title": "MedBioPhys co-op guide",
        "section": "Co-op",
        "summary": "Applications, job categories, and how to position a physics/biology profile.",
        "is_featured": True,
        "source_links": [
            {"label": "Physics undergraduate programs", "url": OFFICIAL_LINKS["physics_programs"]},
            {"label": "Science co-op programs", "url": OFFICIAL_LINKS["science_coop"]},
            {"label": "Prospective co-op students", "url": OFFICIAL_LINKS["science_coop_prospective"]},
            {"label": "Current co-op students", "url": OFFICIAL_LINKS["science_coop_current"]},
        ],
        "body_markdown": """
Physics notes that the co-op version is a five-year program with two eight-month work terms starting in Year 3 and applications due in Year 2. Science Careers describes Science co-op as competitive and based on application, GPA, and interview, with students entering co-op in Year 3 after at least five academic semesters.

## Strong placement categories

Hospital research, medical imaging, health physics, radiation safety, nuclear industry, biotech, academic labs, data science, software/scientific computing, instrumentation, and science communication.

## Resume positioning

Build evidence in three columns: physics/math problem-solving, coding/data/lab tools, and biological/medical context. Employers do not automatically understand MedBioPhys; translate it for them.

## If you do not land early

Do not panic. Use research assistant roles, summer labs, volunteer data projects, open-source analysis, and internal McMaster opportunities to build the same proof points.

## How the sequence changes your planning

Science co-op students enter co-op in Year 3 after completing at least five academic semesters before the first work term, and admission is competitive through application, GPA, and interview. For MedBioPhys students, the practical implication is simple: Level II is not just survival year. It is also resume-building year.

## What employers need translated

Do not assume an employer understands "Medical and Biological Physics." Translate it:

- Physics/math: quantitative modelling, problem solving, uncertainty, instrumentation.
- Computing: Python, data analysis, simulation, image processing, reproducible notebooks.
- Biology/medical: anatomy, biochemistry, radiation, imaging, biological systems.
- Lab: measurement, calibration, reporting, safety, documentation.
- Communication: explaining technical results to scientists, clinicians, engineers, or non-specialists.

## Placement categories to search for

- Hospital research: imaging, radiotherapy, MRI, radiation oncology, clinical data.
- Nuclear and radiation safety: health physics, dosimetry, shielding, compliance, monitoring.
- Biotech/pharma: assay support, data analysis, imaging, quality, technical writing.
- Academic labs: soft matter, molecular biophysics, medical physics, computation.
- Data/software: scientific computing, image analysis, automation, QA tools.
- Science communication and policy: technical documentation, education, outreach, regulatory support.

## Resume bullets that actually work

Weak: "Completed PHYSICS 2G03."

Stronger: "Built Python notebooks to model physical systems, visualize results, and validate outputs against expected limiting cases."

Weak: "Worked in physics lab."

Stronger: "Collected and analyzed experimental data, propagated uncertainty, prepared figures, and wrote formal reports explaining measurement limitations."

Weak: "Interested in medical imaging."

Stronger: "Completed coursework and independent practice in image processing, Fourier/noise concepts, anatomy context, and Python-based analysis."

## Interview prep

Prepare stories for:

- A time your code failed and how you debugged it.
- A lab measurement that did not match expectation.
- A technical concept you explained to a non-specialist.
- A course or project that showed persistence.
- A mistake you caught through checking units, uncertainty, assumptions, or data quality.

## Turning co-op into long-term leverage

During the term, keep a private weekly log of tasks, tools, outcomes, and what you learned. At the end, convert it into:

- Resume bullets.
- A portfolio-safe project summary that does not reveal confidential details.
- A list of skills for grad school/research applications.
- Potential reference-letter talking points.
- Questions for what kind of work you want next.
""",
    },
    {
        "slug": "career-pathways",
        "title": "Career pathways after MedBioPhys",
        "section": "Careers",
        "summary": "Clinical medical physics, health physics, biophysics, imaging AI, nuclear, and adjacent routes.",
        "is_featured": True,
        "source_links": [
            {"label": "Medical Physics - RadGrad", "url": OFFICIAL_LINKS["radgrad_medphys"]},
            {"label": "MAP career opportunities", "url": OFFICIAL_LINKS["map"]},
            {"label": "CCPM certification", "url": OFFICIAL_LINKS["ccpm"]},
            {"label": "Health Canada Radiation Protection Bureau", "url": OFFICIAL_LINKS["health_canada_rpb"]},
        ],
        "body_markdown": """
MAP lists broad graduate outcomes including biophysics, data science/IT, science communication, financial risk analysis, materials innovation, medical physics, nuclear industry, quantum materials, software development, and space industry. The degree is not one job pipeline; it is a technical base.

## Clinical medical physicist

Requires strong physics and anatomy/physiology background, then graduate training, clinical training, and professional accreditation. Course List A is the most relevant undergraduate focus.

## Health physicist / radiation protection

Aim for radiation interactions, detection, safety, regulation, nuclear, dosimetry, communication, and careful lab habits.

## Medical imaging / AI / data

Stack PHYSICS/DATASCI 2G03, imaging courses, statistics, Python, segmentation, reproducible notebooks, and a portfolio.

## Biophysics / soft matter research

Use Course Lists B/C, BIOPHYS 3S03/4S03, molecular/biochemistry electives, advanced lab, computation, and thesis work.

## Clinical medical physics

Clinical medical physicists work around radiation therapy, diagnostic imaging, nuclear medicine, brachytherapy, treatment planning, quality assurance, commissioning, radiation safety, and technology development. McMaster RadGrad describes medical physicists as working in radiotherapy and diagnostic imaging departments with modalities such as external beam therapy, brachytherapy, x-rays, ultrasound, PET, SPECT, and MRI.

Undergrad moves:

- Prioritize Course List A where possible.
- Add anatomy/physiology, radiation, imaging, and computing.
- Seek hospital-adjacent research or medical physics projects.
- Understand that CAMPEP graduate training, residency-style clinical training, and CCPM certification are post-undergrad steps.

## Health physics / radiation protection

Health physics is about protecting people and the environment from ionizing radiation while enabling useful work with radiation sources. Relevant settings include nuclear power, hospitals, universities, research reactors, isotope facilities, regulators, environmental monitoring, decommissioning, and radiation safety offices.

Undergrad moves:

- Take radiation, detection, radioisotope, nuclear, and health physics courses when available.
- Learn dose, shielding, contamination, instrumentation, ALARA, regulatory language, and risk communication.
- Look for co-op or summer work in nuclear, health physics, radiation safety, or isotope labs.

## Imaging / AI / data science

This pathway is strong because MedBioPhys students can combine physics intuition with code and medical context. You are not just "doing AI"; you are learning signal formation, noise, resolution, anatomy, validation, and the limits of data.

Undergrad moves:

- Build Python fluency early.
- Learn image processing: filtering, segmentation, registration, transforms, metrics, and visualization.
- Save clean notebooks and write project summaries.
- Seek MRI/CT/PET/SPECT/ultrasound or radiotherapy data projects where possible.

## Biophysics / soft matter

This route fits students who like living systems but want physical mechanisms: membranes, proteins, condensates, polymers, diffusion, microscopy, scattering, simulations, and statistical mechanics.

Undergrad moves:

- Use Course Lists B/C strategically.
- Pair BIOPHYS courses with biochemistry or advanced physics.
- Find a thesis/summer project early because research evidence matters more than course titles.

## Nuclear / radiation industry

MedBioPhys can also point toward nuclear industry, isotope production, radiation safety, detectors, quality systems, software, and technical operations.

Undergrad moves:

- Build radiation/detection/health physics knowledge.
- Learn technical documentation and safety culture.
- Consider co-op, reactor/isotope-adjacent roles, and instrumentation-heavy projects.

## How to decide

If you like patients/clinical systems but want physics responsibility, investigate clinical medical physics. If you like safety, regulation, measurement, and nuclear/radiation systems, investigate health physics. If you like code and images, build imaging/data proof. If you like mechanisms of life, build biophysics research depth. If you like broad technical work, use co-op and projects to test industry roles.
""",
    },
    {
        "slug": "grad-school-campep-guide",
        "title": "MSc, PhD, CAMPEP, residency, CCPM",
        "section": "Grad School",
        "summary": "The honest roadmap for students considering clinical medical physics in Canada.",
        "is_featured": True,
        "source_links": [
            {"label": "McMaster CAMPEP graduate program", "url": OFFICIAL_LINKS["campep"]},
            {"label": "Medical Physics - RadGrad", "url": OFFICIAL_LINKS["radgrad_medphys"]},
            {"label": "CAMPEP residency applicant information", "url": OFFICIAL_LINKS["campep_residency"]},
            {"label": "Ontario Medical Physics Residency Program", "url": OFFICIAL_LINKS["ontario_residency"]},
            {"label": "CCPM certification", "url": OFFICIAL_LINKS["ccpm"]},
        ],
        "body_markdown": """
McMaster states that Physics & Astronomy offers a CAMPEP-accredited graduate program in medical physics, with thesis-based MSc and PhD streams. The CAMPEP page lists core graduate courses in radiation interactions, radiobiology, imaging systems, radiation detection, advanced radiation physics, radiation oncology physics, professionalism/ethics, and anatomy for medical physicists.

## Undergraduate preparation

Use MedBioPhys to build physics, computation, anatomy/physiology, radiation, imaging, research, and communication. Undergraduate coursework alone does not make you a clinical medical physicist.

## Application signals

Research experience, strong references, coherent course choices, evidence you understand clinical medical physics, and enough coding/statistics to work with modern imaging and treatment data.

## Timeline

By Level II, learn the fields. By Level III, seek research and choose Course List A if clinical medical physics is serious. By Level IV, finish a project, prepare references, and apply to thesis-based programs.

## The honest clinical roadmap

1. Undergraduate degree: build physics, math, computation, anatomy, radiation/imaging, research, and communication.
2. CAMPEP-accredited graduate education or equivalent accredited didactic preparation.
3. Residency-style clinical training, usually in radiation oncology physics, imaging, nuclear medicine, or related areas.
4. Professional certification such as CCPM in Canada, after meeting eligibility and experience requirements.
5. Ongoing clinical competence, quality assurance, safety, research, teaching, and technology adaptation.

## MSc vs PhD

MSc can be the right next step if you want focused research training, a thesis, and a possible bridge into residency or PhD. PhD can be important for research-heavy clinical physics, academic roles, competitive residency applications, and deeper specialization. Direct PhD is a larger commitment and should be chosen for a real research reason, not because it sounds more impressive.

## What graduate programs look for

- Strong physics foundation, not only medical interest.
- Research experience with a supervisor who can write specifically about your work.
- Coding/data competence.
- Evidence you understand what medical physicists actually do.
- Course choices that make sense: radiation, imaging, anatomy, advanced physics, math, computation.
- Clear writing in your statement of interest.

## What to ask programs

- Is the stream CAMPEP-accredited and what exactly is accredited?
- What are residency match outcomes and where are they posted?
- What supervisors are taking students this cycle?
- Are projects clinical, computational, experimental, imaging, radiation therapy, or health-physics oriented?
- How are students funded?
- What coursework is required and how often are courses offered?

## Statement of interest structure

- Opening: your specific medical physics direction.
- Evidence: coursework, research, co-op, code, lab, clinical exposure, or project outputs.
- Fit: why this supervisor/program and which methods/questions interest you.
- Readiness: what skills you bring and what you still need to learn.
- Career direction: clinical physics, research, imaging, radiation therapy, health physics, or uncertainty if honest.

## Interview prep

Be ready to explain:

- A research or course project in plain English.
- Why clinical medical physics is not the same as MRSc radiation therapy.
- A technical challenge you solved.
- Why CAMPEP matters.
- How your undergrad course choices fit the path.
- What you would do if a research project fails or data are messy.

## Undergraduate course priorities

Your course plan should make the graduate-school story obvious. Prioritize modern physics, E&M, quantum, mathematical physics, radiation/radioisotope methodology, imaging, anatomy/physiology, scientific computing, and a senior project if possible. You do not need every possible medical physics elective, but you should avoid a transcript that says "I liked the idea of medical physics" without showing physics depth.

## Research project examples that fit

- Dose calculation, dosimetry, or detector characterization.
- MRI/CT/PET/SPECT image analysis or image-quality work.
- Radiotherapy data analysis, QA automation, or treatment-plan comparison.
- Radiation biology or cell-survival modelling.
- Monte Carlo or simulation-adjacent radiation/imaging work.
- Clinical workflow literature review paired with technical analysis.

## Common traps

- Confusing clinical medical physics with MRSc radiation therapy.
- Assuming a high-level interest in medicine is enough.
- Avoiding hard physics courses because they are risky.
- Applying to supervisors without knowing their modality or methods.
- Waiting until Level IV to learn what CAMPEP, residency, and CCPM mean.

## What to build before applying

By application season, aim to have a tight package: transcript, CV, one-page research summary, code/report/poster artifact if available, two or three strong reference possibilities, and a statement that names the clinical/research problems you actually understand.
""",
    },
    {
        "slug": "cold-email-templates",
        "title": "Cold email templates",
        "section": "Resources",
        "summary": "Reusable outreach patterns for professors, co-op networking, and grad school.",
        "is_featured": False,
        "source_links": [],
        "body_markdown": """
Good outreach is short, specific, and easy to answer.

## Research email structure

- Who you are: program, level, and relevant course/research context.
- Why this person: one specific paper, project, method, or lab theme.
- What you bring: coding, lab, physics, writing, or domain experience.
- Small ask: a short meeting or whether they may consider undergraduates.
- Attachments: resume, transcript, project summary, or GitHub only when useful.

Use the cold email generator for a first draft, then remove anything that sounds generic.

## Research professor email

Subject: Undergraduate research inquiry - [method/topic]

Dear Professor [Name],

I am a Level [II/III/IV] Medical & Biological Physics student interested in [specific area]. I saw that your group works on [specific method/project], and I am especially interested in [concrete reason].

My relevant background is [2-3 courses/skills/artifacts]. I am looking for [summer research / NSERC USRA / thesis supervision / volunteer project] and wondered whether there may be a fit.

I attached my resume and transcript. If you are not taking students, I would appreciate advice on what skills would make me a stronger applicant later.

Best, [Name]

## Co-op networking email

Subject: MedBioPhys co-op student interested in [role/team]

Hello [Name],

I am a Medical & Biological Physics student at McMaster preparing for co-op roles in [imaging/data/radiation safety/biotech/software/research]. My background combines [physics/math], [coding/lab skill], and [medical/biology context].

I noticed [company/lab/team] works on [specific area]. If you have 15 minutes, I would be grateful to ask what skills make students useful in this kind of role and how to position my experience.

Best, [Name]

## Graduate supervisor email

Subject: Prospective MSc/PhD student - [research area]

Dear Professor [Name],

I am applying to [program] for [term/year] and am interested in your work on [specific project/method]. My background includes [research/thesis/co-op/coursework], and I am hoping to pursue graduate research in [specific direction].

Could you let me know whether you anticipate considering new students for [term/year]? I attached my CV, transcript, and a short research summary.

Best, [Name]

## Follow-up email

Subject: Follow-up: undergraduate research inquiry

Dear Professor [Name],

I wanted to briefly follow up on my email below. I know this is a busy time. If there may be a fit, I would be grateful to speak; if not, I appreciate your time and will continue building the relevant skills.

Best, [Name]

## What not to send

- "I am passionate about your research" with no project named.
- A long autobiography.
- Ten professors copied on the same email.
- A request for a job with no evidence of preparation.
- Attachments with unclear filenames.
""",
    },
    {
        "slug": "course-review-guidelines",
        "title": "Course review guidelines",
        "section": "Community",
        "summary": "What students can submit and what Isocentre will not host.",
        "is_featured": False,
        "source_links": [],
        "body_markdown": """
Course reviews should help future students plan without violating academic integrity or copyright.

## Good reviews

- Describe workload patterns, study strategies, pacing, and useful preparation.
- Separate instructor-specific observations from durable course advice.
- Mention whether advice is based on one term or multiple reports.

## Not allowed

- Past tests, assignment solutions, private rubrics, leaked materials, or anything copied from Avenue/private course spaces.
- Personal attacks.
- Advice that encourages academic misconduct.

## Review format that helps most

Useful reviews answer:

- What background made the course easier?
- What should students review before week one?
- What weekly work did the course require?
- What surprised you about assessments?
- What mistakes should future students avoid?
- What did the course unlock later?
- Which pathway is it most useful for?

## Separate durable advice from term-specific details

Instructor, grading scheme, and assessment format can change. Durable advice is usually about preparation, pacing, conceptual bottlenecks, lab/coding habits, and how the course connects to future courses or careers.

## Moderation philosophy

Isocentre should make students more prepared, not more cynical. Reviews should be honest about difficulty and workload, but they should still help a future student act differently.
""",
    },
    {
        "slug": "clinical-medical-physics-roadmap",
        "title": "Clinical medical physics roadmap",
        "section": "Careers",
        "summary": "From MedBioPhys to CAMPEP graduate training, residency, CCPM, and clinical work.",
        "is_featured": True,
        "source_links": [
            {"label": "Medical Physics - RadGrad", "url": OFFICIAL_LINKS["radgrad_medphys"]},
            {"label": "McMaster CAMPEP graduate program", "url": OFFICIAL_LINKS["campep"]},
            {"label": "CAMPEP residency applicant information", "url": OFFICIAL_LINKS["campep_residency"]},
            {"label": "Ontario Medical Physics Residency Program", "url": OFFICIAL_LINKS["ontario_residency"]},
            {"label": "CCPM certification", "url": OFFICIAL_LINKS["ccpm"]},
        ],
        "body_markdown": """
Clinical medical physics is the hospital-facing pathway that many students mean when they say "medical physics." It is not finished at the undergraduate level. MedBioPhys can be an excellent launchpad, but the pathway continues through graduate medical physics education, clinical training, and certification.

## What clinical medical physicists do

They support the safe, accurate, and effective use of physics in medicine. Depending on subfield, that can include radiotherapy treatment planning, external beam therapy, brachytherapy, imaging systems, PET/SPECT, MRI, x-ray imaging, radiation detection, dose measurement, commissioning, quality assurance, and safety.

## Undergrad preparation

- Course List A should be your default focus.
- Build strength in radiation, imaging, anatomy/physiology, modern physics, E&M, computing, and statistics.
- Do a thesis or project if possible.
- Seek hospital-adjacent research, radiotherapy data, imaging analysis, dosimetry, or radiation safety exposure.
- Learn the difference between medical physicist, radiation therapist, dosimetrist, radiologist, and medical radiation technologist.

## Graduate school preparation

McMaster’s Radiation Sciences Graduate Program states that Physics & Astronomy offers a CAMPEP-accredited graduate program in medical physics. Use this as your model for what graduate training contains: radiation interactions, radiobiology, medical imaging systems, radiation detection, advanced radiation physics, radiation oncology physics, professionalism/ethics, and anatomy for medical physicists.

## Residency and certification

CAMPEP residency information emphasizes a strong foundation in basic physics. Canadian clinical certification commonly points students toward CCPM after appropriate graduate and clinical experience. Ontario also has a recognized medical physics residency pathway. The key student takeaway is that residency is competitive and clinical experience is not interchangeable with simply taking undergraduate medical physics courses.

## Level-by-level actions

- Level I: protect physics/math; understand MRSc vs medical physics.
- Level II: perform well in modern physics, lab, computing, differential equations; start research outreach.
- Level III: choose Course List A, add imaging/radiation/anatomy, seek supervisor fit.
- Level IV: complete thesis/project, request references, write a clear statement of interest.
- After graduation: apply to CAMPEP graduate programs or aligned research programs with a credible clinical physics story.

## Strong application evidence

- A research supervisor who can describe your actual work.
- A project involving imaging, radiation, dosimetry, detection, clinical data, or physics modelling.
- Clean technical writing and figures.
- Python/MATLAB/data analysis ability.
- A statement that understands clinical responsibility and patient-safety culture.
""",
    },
    {
        "slug": "health-physics-radiation-protection",
        "title": "Health physics and radiation protection",
        "section": "Careers",
        "summary": "Radiation safety, nuclear industry, regulatory work, monitoring, shielding, and risk communication.",
        "is_featured": False,
        "source_links": [
            {"label": "Health Canada Radiation Protection Bureau", "url": OFFICIAL_LINKS["health_canada_rpb"]},
            {"label": "Science co-op programs", "url": OFFICIAL_LINKS["science_coop"]},
            {"label": "MAP career opportunities", "url": OFFICIAL_LINKS["map"]},
        ],
        "body_markdown": """
Health physics is the radiation protection pathway: measuring, controlling, explaining, and regulating radiation risk. It is relevant in hospitals, universities, nuclear power, isotope production, research reactors, environmental monitoring, decommissioning, and government/regulatory settings.

## What the work looks like

- Dose monitoring and interpretation.
- Shielding and source-use planning.
- Contamination surveys and instrument checks.
- Radiation safety training.
- Procedure writing and compliance documentation.
- Emergency planning and risk communication.
- Environmental and occupational radiation protection.

## Course strategy

Prioritize radiation and detection courses: MEDPHYS 4B03, 4RA3/4RB3, 4F03, MEDPHYS 3C03, PHYSICS 4E03, and relevant labs/projects when available. Pair this with strong lab habits, uncertainty, statistics, and communication.

## Skills to build

- Radiation units and conversions.
- Detector types and limitations.
- ALARA reasoning.
- Shielding intuition.
- Regulatory vocabulary.
- Clear writing for non-specialists.
- Calm explanation of risk.

## Experience to seek

Co-op and summer roles can matter a lot: nuclear industry, radiation safety offices, isotope labs, hospital radiation protection, research reactor-adjacent work, environmental monitoring, and instrumentation projects.

## How to position yourself

Say: "I am building a radiation protection profile through medical/biological physics, radiation coursework, scientific computing, lab measurement, uncertainty analysis, and safety-focused communication."

## Course and project combinations

Strong combinations include radiation interactions plus lab/instrumentation, radioisotope methodology plus health physics, nuclear/particle physics plus shielding/detection, and scientific computing plus detector/data analysis. If you can add co-op or summer work in a radiation safety office, nuclear setting, isotope lab, or hospital environment, your profile becomes much clearer.

## Portfolio artifacts

- A radiation unit and detector comparison sheet.
- A shielding calculation walkthrough with assumptions stated.
- A contamination survey or instrument QA mock procedure using public/synthetic data.
- A short explainer on ALARA for non-specialists.
- A Python notebook modelling exponential decay, detector response, or dose-rate falloff.

## Interview stories to prepare

- A time you found an error through units or calibration logic.
- How you would explain radiation risk without either minimizing or exaggerating it.
- How you handle procedure-driven work.
- A lab or project where documentation mattered.
- Why safety culture is technical work, not just paperwork.

## Where MedBioPhys helps

You bring more than biology context. You bring measurement, uncertainty, modelling, code, and an ability to translate between physics and human systems. That translation is central to radiation protection work.
""",
    },
    {
        "slug": "medical-imaging-ai-portfolio",
        "title": "Medical imaging, AI, and data portfolio",
        "section": "Careers",
        "summary": "How to turn MedBioPhys into imaging/data evidence for research, co-op, grad school, or industry.",
        "is_featured": False,
        "source_links": [
            {"label": "Medical Physics - RadGrad", "url": OFFICIAL_LINKS["radgrad_medphys"]},
            {"label": "MAP Honours Medical and Biological Physics", "url": OFFICIAL_LINKS["map"]},
        ],
        "body_markdown": """
Imaging/data is one of the most natural MedBioPhys directions because it rewards physics intuition and coding together. The goal is not to call everything AI. The goal is to understand image formation, noise, resolution, anatomy, validation, and clinical/research constraints.

## Core technical stack

- Python, NumPy, pandas, matplotlib, scikit-image, basic PyTorch or TensorFlow if needed.
- Image processing: filtering, thresholding, segmentation, registration, interpolation, transforms, metrics.
- Scientific computing habits: clean notebooks, reproducible environments, version control, readable plots.
- Statistics: train/test splits, overfitting, uncertainty, sensitivity/specificity, Dice/Jaccard, ROC/AUC where appropriate.

## Physics concepts that matter

- Signal, noise, resolution, contrast, artifacts.
- Fourier thinking.
- Attenuation, scattering, relaxation, detection, reconstruction.
- Dose and safety where ionizing imaging is involved.

## Portfolio projects

- Segment an open medical image dataset and write a validation note.
- Compare denoising methods and discuss artifacts.
- Simulate a simple imaging system or point-spread function.
- Reproduce a figure from a medical imaging paper using public data.
- Build a small radiotherapy or imaging QA analysis notebook with synthetic/public data.

## What makes a portfolio credible

- Clear README.
- Data source and license stated.
- Methods explained in plain English.
- Plots with captions and units.
- Limitations section.
- No private patient data or course materials.

## Courses and experiences to prioritize

PHYSICS/DATASCI 2G03, MEDPHYS 4D03, medical physics/radiation courses, statistics/data electives where possible, anatomy, and any imaging or computational research project.

## A staged portfolio plan

### Level II

Build clean Python habits. Save one polished notebook from scientific computing. Learn how to read, reshape, plot, and sanity-check arrays. Practice explaining what a figure means physically.

### Level III

Add domain context: Fourier ideas, image formation, noise, anatomy, radiation/imaging physics, and statistics. Start one public-data project or research assistant task.

### Level IV

Make the work application-ready: README, methods, results, limitations, and a short project page. If doing a thesis, maintain a portfolio-safe summary that avoids confidential data.

## What not to do

- Do not upload private patient data.
- Do not upload course solutions or private assignment material.
- Do not present a model as clinically useful without validation.
- Do not hide failed assumptions; limitations make a project more credible.

## Project ideas by pathway

- Clinical medical physics: image quality analysis, synthetic CT/radiotherapy data tools, QA dashboards.
- Biophysics: microscopy segmentation, diffusion simulation, particle tracking, membrane image analysis.
- Health physics: dose-rate simulation, detector calibration curves, radiation-monitoring visualizations.
- Industry/co-op: automated report generation, reproducible plotting, data-cleaning pipelines.

## What reviewers like to see

Clear problem statement, readable code, appropriate metrics, honest limitations, and enough physics explanation that the project is not just a machine-learning demo.
""",
    },
    {
        "slug": "nserc-usra-and-summer-research",
        "title": "NSERC USRA and summer research guide",
        "section": "Research",
        "summary": "How to find a supervisor, prepare a strong application, and use summer research well.",
        "is_featured": True,
        "source_links": [
            {"label": "McMaster USRA", "url": OFFICIAL_LINKS["mcmaster_usra"]},
            {"label": "NSERC USRA", "url": OFFICIAL_LINKS["nserc_usra"]},
            {"label": "Upper-year research projects", "url": OFFICIAL_LINKS["research_projects"]},
        ],
        "body_markdown": """
Summer research can change the entire MedBioPhys path because it turns interest into evidence. NSERC USRA is a major funded route if you are eligible and a supervisor supports the application, but it is not the only route.

## Timeline

- November/December: identify areas and professors.
- January: prepare resume, transcript, and short project-fit paragraphs.
- January/February: send targeted emails.
- February/March: follow department/supervisor application instructions.
- Spring/Summer: track outputs weekly.

## Strong application ingredients

- Supervisor fit.
- Clear technical readiness.
- Specific research interest.
- Strong enough academic record for the competition.
- Evidence beyond grades: coding, lab reports, BIOPHYS topic, literature review, project notebook.

## Alternatives if USRA does not happen

- Paid research assistant.
- SURA/internal award.
- Volunteer research with clear scope.
- Reading project.
- Co-op placement.
- Self-directed portfolio project with public data/code.

## How to use the summer

Do not only "help in the lab." Leave with artifacts: poster, abstract, figures, code, methods writeup, literature map, supervisor reference, or thesis continuation plan.

## Email strategy

Send fewer, better emails. A good email names the professor's area, explains the method or question you want to learn, gives evidence of preparation, and makes a small ask. If you have no evidence yet, build one first: a one-page literature map, a code notebook, or a short summary of a course project.

## What to include

- Resume.
- Unofficial transcript if requested or appropriate.
- Availability window.
- Relevant courses.
- One sentence on why that specific lab.
- One sentence on what you can do now.
- One sentence on what you want to learn.

## What supervisors are evaluating

They are not only evaluating grades. They are asking whether you will be reliable, teachable, careful with data/materials, able to communicate, and likely to produce useful work in 14-16 weeks.

## If you get the position

Set expectations early: meeting rhythm, deliverables, data/code storage, authorship/poster possibilities, safety/training requirements, and what to do when blocked. Keep a weekly log from day one.

## If you do not get the position

Ask what would make you competitive next time. Then build it. A self-directed project, course review, coding artifact, or reading summary can be enough to make the next email stronger.
""",
    },
    {
        "slug": "thesis-and-senior-project-guide",
        "title": "Thesis and senior project guide",
        "section": "Research",
        "summary": "How to choose a supervisor, scope a project, and turn final-year research into proof.",
        "is_featured": False,
        "source_links": [{"label": "Upper-year research projects", "url": OFFICIAL_LINKS["research_projects"]}],
        "body_markdown": """
The senior project can be the strongest part of a MedBioPhys degree if you choose it deliberately. It can become your writing sample, poster, oral presentation, technical story, and best reference letter.

## Choose by fit, not title

Ask whether the project is coding-heavy, wet-lab, data-analysis, instrumentation, theory, literature-review, clinical-data-adjacent, or experimental. A glamorous title with a poor weekly fit is worse than a modest project with strong supervision and clear outputs.

## Questions before committing

- What is the expected final deliverable?
- Who will supervise weekly work?
- What skills should I learn before the start?
- What data/materials/tools will I use?
- What does success look like by month one, month three, and final submission?
- Is there poster, conference, or publication potential?

## Project operating system

- Keep a weekly log.
- Write methods as you go.
- Save clean figures and captions.
- Meet regularly and bring specific blockers.
- Make a thesis one-pager by the end of the first month.

## Turning it into applications

For grad school: emphasize question, method, independence, and supervisor fit. For co-op/industry: emphasize tools, outputs, teamwork, documentation, and problem-solving. For clinical medical physics: connect the physics method to patient safety, imaging, radiation, measurement, or clinical workflow where honest.

## Types of projects

- Experimental: measurement, calibration, instrumentation, sample prep, uncertainty, troubleshooting.
- Computational: simulation, modelling, image analysis, data pipelines, statistics.
- Literature/review: synthesis of a narrow research area with a clear technical question.
- Clinical/data-adjacent: imaging, radiation, QA, workflow, retrospective analysis where allowed.
- Theory: mathematical models, derivations, numerical experiments, interpretation.

## Red flags before committing

- No clear supervisor or graduate-student contact.
- No realistic deliverable.
- Required skills are far beyond what you can learn in time.
- The project depends on data or equipment that may not arrive.
- You cannot explain why the topic fits your goals.

## First-month checklist

- Write a one-paragraph project scope.
- Create a reading list.
- Define the first output.
- Set meeting cadence.
- Decide where notes/code/data live.
- Learn required safety or ethics constraints.
- Identify what "done enough" looks like for the term.

## Final-month checklist

- Freeze analysis enough to write.
- Make figures publication/poster clean where possible.
- Ask for feedback early.
- Prepare a plain-English summary.
- Ask your supervisor what they can honestly say in a reference letter.
""",
    },
]


SOURCE_CALENDAR = [{"label": "2025-2026 Undergraduate Calendar", "url": OFFICIAL_LINKS["calendar"]}]
SOURCE_MAP = [{"label": "MAP Honours Medical and Biological Physics", "url": OFFICIAL_LINKS["map"]}]


COURSE_SPECS = [
    ("MEDPHYS1A03", "Physics in Medicine and Biology", "MEDPHYS", 1, ["admission-modern", "recommended-level-i"], ["medical-physics", "imaging"]),
    ("PHYSICS1A03", "Introductory Physics", "PHYSICS", 1, ["admission-physics"], ["physics-foundation"]),
    ("PHYSICS1V03", "Introductory Physics", "PHYSICS", 1, ["admission-physics"], ["physics-foundation"]),
    ("PHYSICS1C03", "Physics for the Chemical and Physical Sciences", "PHYSICS", 1, ["admission-physics"], ["physics-foundation"]),
    ("PHYSICS1D03", "Introductory Mechanics", "PHYSICS", 1, ["admission-physics"], ["physics-foundation"]),
    ("PHYSICS1AA3", "Introduction To Modern Physics", "PHYSICS", 1, ["admission-modern"], ["physics-foundation", "medical-physics"]),
    ("PHYSICS1CC3", "Modern Physics for the Chemical and Physical Sciences", "PHYSICS", 1, ["admission-modern", "recommended-level-i"], ["physics-foundation", "medical-physics"]),
    ("PHYSICS1E03", "Waves, Electricity and Magnetic Fields", "PHYSICS", 1, ["admission-modern"], ["physics-foundation"]),
    ("MATH1A03", "Calculus For Science I", "MATH", 1, ["admission-math"], ["math-foundation"]),
    ("MATH1AA3", "Calculus For Science II", "MATH", 1, ["admission-math"], ["math-foundation"]),
    ("MATH1LS3", "Calculus for the Life Sciences I", "MATH", 1, ["admission-math"], ["math-foundation"]),
    ("MATH1LT3", "Calculus for the Life Sciences II", "MATH", 1, ["admission-math"], ["math-foundation"]),
    ("MATH1X03", "Calculus for Math and Stats I", "MATH", 1, ["admission-math"], ["math-foundation"]),
    ("MATH1XX3", "Calculus for Math and Stats II", "MATH", 1, ["admission-math"], ["math-foundation"]),
    ("MATH1B03", "Linear Algebra I", "MATH", 1, ["admission-bio-chem-math", "required-by-level-ii"], ["math-foundation", "data-ai"]),
    ("CHEM1A03", "Introductory Chemistry I", "CHEM", 1, ["admission-chemistry"], ["life-science"]),
    ("CHEM1AA3", "Introductory Chemistry II", "CHEM", 1, ["admission-bio-chem-math", "required-by-level-ii"], ["life-science"]),
    ("BIOLOGY1A03", "Cellular and Molecular Biology", "BIOLOGY", 1, ["admission-bio-chem-math", "required-by-level-ii"], ["biological-physics"]),
    ("BIOLOGY1M03", "Biodiversity, Evolution and Humanity", "BIOLOGY", 1, ["recommended-level-i"], ["biological-physics"]),
    ("PHYSICS2C03", "Modern Physics", "PHYSICS", 2, ["level-ii-required"], ["medical-physics", "physics-foundation"]),
    ("PHYSICS2P03", "Introductory Laboratory", "PHYSICS", 2, ["level-ii-required"], ["research", "instrumentation"]),
    ("PHYSICS2G03", "Scientific Computing", "PHYSICS", 2, ["level-ii-computing"], ["data-ai", "research"]),
    ("DATASCI2G03", "Scientific Computing", "DATASCI", 2, ["level-ii-computing"], ["data-ai", "research"]),
    ("MATH2C03", "Introduction to Differential Equations", "MATH", 2, ["level-ii-required"], ["math-foundation", "medical-physics"]),
    ("MATH2X03", "Advanced Calculus I", "MATH", 2, ["level-ii-calculus"], ["math-foundation"]),
    ("MATH2MC3", "Multivariable Calculus", "MATH", 2, ["level-ii-calculus"], ["math-foundation"]),
    ("MATH2XA3", "Vector Calculus I", "MATH", 2, ["level-ii-calculus"], ["math-foundation"]),
    ("BIOPHYS2S03", "Explorations in Medical and Biological Physics", "BIOPHYS", 2, ["level-ii-required"], ["research", "biological-physics", "medical-physics"]),
    ("KINESIOL2X03", "Human Anatomy and Physiology I", "KINESIOL", 2, ["required-by-graduation"], ["medical-physics", "clinical"]),
    ("KINESIOL2Y03", "Human Anatomy and Physiology I", "KINESIOL", 2, ["required-by-graduation"], ["medical-physics", "clinical"]),
    ("KINESIOL2XX3", "Human Anatomy and Physiology II", "KINESIOL", 2, ["course-list-a"], ["medical-physics", "clinical"]),
    ("KINESIOL2YY3", "Human Anatomy and Physiology II", "KINESIOL", 2, ["course-list-a"], ["medical-physics", "clinical"]),
    ("BIOCHEM2B03", "Nucleic Acid Structure and Function", "BIOCHEM", 2, ["biochem-option"], ["biological-physics"]),
    ("BIOCHEM2BB3", "Protein Structure and Enzyme Function", "BIOCHEM", 2, ["biochem-option"], ["biological-physics"]),
    ("BIOCHEM2EE3", "Metabolism and Physiological Chemistry", "BIOCHEM", 2, ["biochem-option", "recommended-biochem"], ["biological-physics"]),
    ("BIOCHEM3G03", "Proteins and Nucleic Acids", "BIOCHEM", 3, ["biochem-option", "recommended-biochem"], ["biological-physics"]),
    ("PHYSICS2B03", "Electricity and Magnetism I", "PHYSICS", 3, ["level-iii-required"], ["physics-foundation", "medical-physics"]),
    ("PHYSICS3K03", "Thermodynamics and Statistical Mechanics", "PHYSICS", 3, ["level-iii-required"], ["soft-matter", "biological-physics"]),
    ("MATH3C03", "Mathematical Physics I", "MATH", 3, ["level-iii-required"], ["math-foundation", "physics-foundation"]),
    ("BIOPHYS3S03", "'Squishy Physics': Physics of Soft Matter", "BIOPHYS", 3, ["level-iii-required", "course-list-c"], ["soft-matter"]),
    ("MEDPHYS4B03", "Radioactivity and Radiation in Medical Physics", "MEDPHYS", 3, ["level-iii-required", "course-list-a"], ["medical-physics", "health-physics"]),
    ("BIOPHYS4S03", "Introduction to Molecular Biophysics", "BIOPHYS", 4, ["level-iv-required"], ["biological-physics", "soft-matter"]),
    ("MEDPHYS4RA3", "Radiation and Radioisotope Methodology I", "MEDPHYS", 4, ["level-iv-required", "course-list-a"], ["medical-physics", "health-physics"]),
    ("MEDPHYS4RB3", "Radiation and Radioisotope Methodology II", "MEDPHYS", 4, ["course-list-a"], ["medical-physics", "health-physics"]),
    ("MEDPHYS4T03", "Clinical Applications of Physics in Medicine", "MEDPHYS", 4, ["level-iv-required", "course-list-a"], ["medical-physics", "clinical"]),
    ("PHYSICS3MM3", "Quantum Mechanics I", "PHYSICS", 4, ["level-iv-required"], ["physics-foundation"]),
    ("CHEM3RC3", "Radioisotopes in Medicine", "CHEM", 3, ["course-list-a"], ["medical-physics", "health-physics"]),
    ("MEDPHYS3C03", "Operational Health Physics: Laboratory & Communication", "MEDPHYS", 3, ["course-list-a"], ["health-physics", "radiation-safety"]),
    ("MEDPHYS4D03", "Imaging in Medicine and Biology", "MEDPHYS", 4, ["course-list-a"], ["medical-physics", "imaging", "data-ai"]),
    ("MEDPHYS4F03", "Fundamentals of Health Physics", "MEDPHYS", 4, ["course-list-a"], ["health-physics", "radiation-safety"]),
    ("MEDPHYS4I03", "Introduction to Biophotonics", "MEDPHYS", 4, ["course-list-a"], ["imaging", "biological-physics"]),
    ("MEDPHYS4U03", "Radiation Biology", "MEDPHYS", 4, ["course-list-a"], ["medical-physics", "radiation-biology"]),
    ("MEDPHYS4Y06", "Advanced Medical Physics Project", "MEDPHYS", 4, ["course-list-a"], ["medical-physics", "research"]),
    ("PHYSICS4E03", "Particle and Nuclear Physics", "PHYSICS", 4, ["course-list-a"], ["health-physics", "nuclear"]),
    ("PHYSICS4P06", "Senior Research Project", "PHYSICS", 4, ["course-list-a", "research"], ["research", "grad-school"]),
    ("BIOCHEM2L06", "Inquiry in Biochemical Techniques", "BIOCHEM", 2, ["course-list-b"], ["biological-physics", "wet-lab"]),
    ("BIOCHEM3BP3", "Practical Bioinformatics in the Genomics Era", "BIOCHEM", 3, ["course-list-b"], ["biological-physics", "data-ai"]),
    ("BIOCHEM3D03", "Metabolism and Regulation", "BIOCHEM", 3, ["course-list-b"], ["biological-physics"]),
    ("BIOCHEM3MI3", "Microbial Interactions", "BIOCHEM", 3, ["course-list-b"], ["biological-physics"]),
    ("BIOCHEM3Z03", "Structural Determination and Analysis of Macromolecules", "BIOCHEM", 3, ["course-list-b"], ["biological-physics"]),
    ("BIOCHEM4E03", "Gene Regulation in Stem Cells and Development", "BIOCHEM", 4, ["course-list-b"], ["biological-physics"]),
    ("BIOCHEM4H03", "Biotechnology and Drug Discovery", "BIOCHEM", 4, ["course-list-b"], ["biological-physics", "industry"]),
    ("BIOCHEM4M03", "Cellular and Integrated Metabolism", "BIOCHEM", 4, ["course-list-b"], ["biological-physics"]),
    ("BIOCHEM4N03", "Molecular Membrane Biology", "BIOCHEM", 4, ["course-list-b"], ["biological-physics", "soft-matter"]),
    ("BIOCHEM4Q03", "Biochemical Pharmacology", "BIOCHEM", 4, ["course-list-b"], ["biological-physics", "industry"]),
    ("BIOLOGY2B03", "Cell Biology", "BIOLOGY", 2, ["course-list-b"], ["biological-physics"]),
    ("BIOPHYS3D03", "Origin of Life", "BIOPHYS", 3, ["course-list-b"], ["biological-physics"]),
    ("BIOPHYS3G03", "Modelling Life", "BIOPHYS", 3, ["course-list-b"], ["biological-physics", "data-ai"]),
    ("BIOPHYS4P06", "Senior Project in Biophysics", "BIOPHYS", 4, ["course-list-c", "research"], ["soft-matter", "research"]),
    ("PHYSICS2BB3", "Electricity and Magnetism II", "PHYSICS", 2, ["course-list-c"], ["physics-foundation"]),
    ("PHYSICS3D03", "Inquiry in Physics", "PHYSICS", 3, ["course-list-c"], ["research"]),
    ("PHYSICS3N04", "Physical Optics", "PHYSICS", 3, ["course-list-c"], ["imaging", "instrumentation"]),
    ("PHYSICS3P03", "Advanced Laboratory", "PHYSICS", 3, ["course-list-c"], ["research", "instrumentation"]),
    ("PHYSICS4F03", "Quantum Mechanics II", "PHYSICS", 4, ["course-list-c"], ["physics-foundation"]),
    ("PHYSICS4G03", "Computational Physics", "PHYSICS", 4, ["course-list-c"], ["data-ai", "research"]),
    ("PHYSICS4K03", "Physics of Quantum Matter", "PHYSICS", 4, ["course-list-c"], ["soft-matter", "physics-foundation"]),
]


SPECIFIC = {
    "PHYSICS2G03": ("Start Python early, especially arrays, plotting, functions, and debugging. Keep assignments in a clean repo.", "Debugging at the end, unclear units, and plots with no physical interpretation.", "Make tiny test cases before the full simulation. Explain every graph in a caption."),
    "DATASCI2G03": ("Treat this as the coding backbone for imaging, simulations, and research automation.", "Copying notebook patterns without understanding data structures.", "Write reusable functions and keep a portfolio-quality notebook."),
    "PHYSICS2P03": ("Review uncertainty, fitting, residuals, significant figures, and report structure.", "Collecting data without enough notes to defend the analysis.", "Draft methods and analysis the same day as the lab."),
    "PHYSICS2B03": ("Review vectors, fields, line/surface/volume integrals, and electrostatics.", "Skipping the geometry setup and trying to force formulas.", "Draw the field geometry first, then choose coordinates."),
    "BIOPHYS2S03": ("Come ready to connect physics methods to messy biological systems.", "Treating microscopy, diffusion, modelling, and biology as disconnected facts.", "For each unit, write the physical model and the biological question it answers."),
    "MEDPHYS4B03": ("Know exponential decay, interactions of radiation with matter, units, and uncertainty.", "Mixing up activity, dose, exposure, and energy-deposition concepts.", "Make a radiation-units sheet and update it every week."),
    "MEDPHYS4D03": ("Review Fourier ideas, image formation, noise, resolution, and Python basics.", "Learning modality facts without linking them to signal formation.", "Compare modalities by source, detector, contrast mechanism, resolution, dose, and artifacts."),
    "MEDPHYS4F03": ("Review radiation interactions, shielding logic, and regulatory vocabulary.", "Treating safety as memorization instead of risk reasoning.", "Practice explaining risk and controls to a non-physicist."),
    "MEDPHYS4T03": ("Bring radiation, imaging, anatomy, and clinical workflow context together.", "Confusing medical physicist, radiation therapist, radiologist, and dosimetrist roles.", "Map each clinical task to the physics responsibility behind it."),
    "PHYSICS4P06": ("Start supervisor conversations months early and clarify deliverables.", "Choosing a project only by topic, not by weekly work style or supervision fit.", "Treat poster, talk, report, and reference letter as project outputs from day one."),
}


def build_course(spec):
    code, title, category, level, roles, tracks = spec
    prep, failure, strategy = SPECIFIC.get(
        code,
        generic_advice(category, tracks, roles),
    )
    return {
        "code": code,
        "title": title,
        "official_title": title,
        "category": category,
        "level": level,
        "units": 6 if code.endswith("06") else 3,
        "calendar_url": OFFICIAL_LINKS["calendar"],
        "source_urls": SOURCE_CALENDAR,
        "aliases": alias_variants(code),
        "requirement_roles": roles,
        "track_tags": tracks,
        "official_notes": official_note_for(roles, tracks),
        "description": description_for(title, category, roles, tracks),
        "difficulty": rating_for(category, roles, "difficulty"),
        "workload": rating_for(category, roles, "workload"),
        "math_intensity": rating_for(category, roles, "math"),
        "coding_intensity": 4 if "data-ai" in tracks else (2 if "research" in tracks else 1),
        "memorization_intensity": 5 if category in {"BIOCHEM", "BIOLOGY", "KINESIOL"} else (3 if category in {"MEDPHYS", "CHEM"} else 2),
        "before_starting": prep,
        "resources": resources_for(category, tracks),
        "failure_points": failure,
        "study_strategy": strategy,
        "unlocks": unlocks_for(tracks, roles),
        "pair_with": pairings_for(tracks, roles),
        "student_tips": student_tip_for(category, tracks),
        "student_reported": "Student-reported advice should be treated as unofficial and term-dependent. Use course reviews below for lived experience once moderated submissions arrive.",
        "last_verified_at": datetime.now(timezone.utc),
    }


def generic_advice(category, tracks, roles):
    if category in {"BIOCHEM", "BIOLOGY", "KINESIOL"}:
        return (
            "Use active recall from week one and translate every pathway, system, or mechanism into a blank-page diagram.",
            "Passive rereading and late memorization. These courses punish students who study them like physics problem sets.",
            "Use spaced repetition, diagrams, and explain-back practice; reserve problem-set time for physics/math courses.",
        )
    if category in {"MATH"}:
        return (
            "Review algebra, calculus, vectors, complex numbers, and proof/definition habits depending on the course.",
            "Choosing techniques by pattern matching instead of identifying the mathematical structure first.",
            "Build a method map: problem type, assumptions, allowed tools, and one solved example.",
        )
    if category in {"MEDPHYS", "CHEM"} or "medical-physics" in tracks:
        return (
            "Review units, dimensional analysis, exponential processes, anatomy context, and the physics mechanism behind each application.",
            "Memorizing clinical or radiation terms without linking them to measurable physical quantities.",
            "Make comparison tables by modality, source, interaction, detector, risk, and clinical use.",
        )
    return (
        "Review the prerequisite physics and math before the term starts; upper-year physics compounds quickly.",
        "Starting assignments late and treating derivations as formulas instead of reasoning tools.",
        "Work problems in layers: concept, diagram, coordinates, equation, units, interpretation.",
    )


def description_for(title, category, roles, tracks):
    role_text = "official requirement" if any("required" in role for role in roles) else "pathway elective"
    track_text = ", ".join(tracks[:3]) if tracks else category.lower()
    return f"{title} is a {role_text} or planning-relevant course for {track_text}. The guide explains where it fits, how to prepare, and how students can use it later."


def official_note_for(roles, tracks):
    notes = []
    if "course-list-a" in roles:
        notes.append("Calendar Course List A: Medical Physics Focus.")
    if "course-list-b" in roles:
        notes.append("Calendar Course List B: Biological Physics Focus.")
    if "course-list-c" in roles:
        notes.append("Calendar Course List C: Physics of Soft Matter Focus.")
    if "level-ii-required" in roles or "level-iii-required" in roles or "level-iv-required" in roles:
        notes.append("Listed in the 2025-2026 Honours Medical and Biological Physics requirements.")
    if "admission" in " ".join(roles):
        notes.append("Listed in the 2025-2026 Level II admission requirements or notes.")
    return " ".join(notes) or "Relevant to MedBioPhys planning; confirm prerequisites, antirequisites, and offering status in the official calendar and course outlines."


def rating_for(category, roles, kind):
    base = 3
    if category in {"PHYSICS", "MATH"}:
        base = 4
    if category in {"BIOCHEM", "KINESIOL"} and kind in {"workload", "difficulty"}:
        base = 4
    if "level-iv-required" in roles or "course-list-c" in roles:
        base += 1 if kind in {"difficulty", "math"} else 0
    if kind == "math" and category in {"BIOCHEM", "BIOLOGY", "KINESIOL"}:
        return 1
    if kind == "workload" and any(role in roles for role in ["research", "course-list-a", "course-list-b", "course-list-c"]):
        return min(5, base)
    return max(1, min(5, base))


def resources_for(category, tracks):
    resources = ["official calendar", "current course outline", "office hours"]
    if category in {"PHYSICS", "MATH"}:
        resources += ["worked examples", "problem sets", "formula/concept sheet"]
    if "data-ai" in tracks:
        resources += ["Python docs", "NumPy/SciPy examples", "version-controlled notebooks"]
    if category in {"BIOCHEM", "BIOLOGY", "KINESIOL"}:
        resources += ["active recall", "diagrams", "spaced repetition"]
    if "medical-physics" in tracks or "health-physics" in tracks:
        resources += ["radiation unit tables", "modality comparison charts"]
    return ", ".join(resources) + "."


def unlocks_for(tracks, roles):
    mapping = {
        "medical-physics": "clinical medical physics, imaging, radiation therapy physics, CAMPEP-facing preparation",
        "health-physics": "radiation protection, nuclear industry, dosimetry, and safety communication",
        "biological-physics": "molecular biophysics, biochemistry-facing research, biotechnology, and wet/dry lab collaboration",
        "soft-matter": "soft condensed matter, membranes, polymers, complex fluids, and physics-forward graduate work",
        "data-ai": "imaging AI, scientific computing, data analysis, simulation, and portfolio projects",
        "research": "summer research, thesis/senior projects, supervisor conversations, and graduate applications",
    }
    values = [mapping[tag] for tag in tracks if tag in mapping]
    if not values:
        values = ["stronger prerequisite preparation and better upper-year course flexibility"]
    return "; ".join(values) + "."


def pairings_for(tracks, roles):
    if "medical-physics" in tracks:
        return "Pair with anatomy/physiology, MEDPHYS radiation/imaging courses, and a research or hospital-facing project."
    if "data-ai" in tracks:
        return "Pair with Python, statistics, image-processing projects, and a GitHub portfolio."
    if "biological-physics" in tracks:
        return "Pair with biochemistry, cell biology, molecular biophysics, and lab/research experience."
    if "soft-matter" in tracks:
        return "Pair with thermodynamics/stat mech, advanced lab, computation, and soft matter research."
    return "Pair with the requirement checker and official course outlines before registration."


def student_tip_for(category, tracks):
    if "data-ai" in tracks:
        return "A clean notebook or small repo can become interview evidence; do not leave code trapped in one-off assignments."
    if "medical-physics" in tracks:
        return "Always connect the equation to patient workflow, measurement, dose, image quality, or safety."
    if category in {"BIOCHEM", "BIOLOGY", "KINESIOL"}:
        return "Use active recall early; content volume is the main risk."
    if category == "MATH":
        return "Definitions and setup matter more than memorizing final forms."
    return "Start from the physical picture before the algebra."


def alias_variants(code):
    prefix = "".join([c for c in code if c.isalpha()])
    number = code.replace(prefix, "")
    return [f"{prefix} {number}", code]


COURSES = [build_course(spec) for spec in COURSE_SPECS]


REQUIREMENT_RULES = [
    ("level-ii-admission", "gpa-minimum", "Minimum GPA 5.0", "The official calendar lists a Grade Point Average of at least 5.0 for admission.", [], "advisor", 0, 0, 1, "", "Confirm GPA and competitive context with official advising.", 1),
    ("level-ii-admission", "admission-math-6-units", "6 units first-year math", "Complete 6 units from approved first-year calculus/math courses.", ["MATH1A03", "MATH1AA3", "MATH1LS3", "MATH1LT3", "MATH1X03", "MATH1XX3", "MATH1ZA3", "MATH1ZB3"], "units", 0, 6, 3, "", "Two 3-unit courses from this group are required.", 2),
    ("level-ii-admission", "admission-physics-3-units", "3 units intro physics/mechanics", "Complete 3 units from PHYSICS 1A03, 1C03, 1D03, or 1V03.", ["PHYSICS1A03", "PHYSICS1C03", "PHYSICS1D03", "PHYSICS1V03"], "units", 0, 3, 3, "", "PHYSICS 1V03 is the online version of PHYSICS 1A03 when offered.", 3),
    ("level-ii-admission", "admission-modern-3-units", "3 units MEDPHYS/modern physics group", "Complete 3 units from MEDPHYS 1A03, PHYSICS 1AA3, 1CC3, or 1E03.", ["MEDPHYS1A03", "PHYSICS1AA3", "PHYSICS1CC3", "PHYSICS1E03"], "units", 0, 3, 3, "", "MEDPHYS 1A03 and PHYSICS 1CC3 are recommended in Level I by the calendar notes.", 4),
    ("level-ii-admission", "admission-chem-3-units", "3 units chemistry", "Complete CHEM 1A03 or CHEM 1E03.", ["CHEM1A03", "CHEM1E03"], "units", 0, 3, 3, "", "CHEM 1AA3 is separately required by end of Level II if not completed earlier.", 5),
    ("level-ii-admission", "admission-bio-chem-math-3-units", "3 units biology/CHEM 1AA3/linear algebra group", "Complete 3 units from BIOLOGY 1A01/1A02/1A03, CHEM 1AA3, MATH 1B03, or MATH 1ZC3.", ["BIOLOGY1A01", "BIOLOGY1A02", "BIOLOGY1A03", "CHEM1AA3", "MATH1B03", "MATH1ZC3"], "units", 0, 3, 3, "", "BIOLOGY 1A01 and 1A02 together substitute for BIOLOGY 1A03; confirm details with the calendar.", 6),
    ("level-ii-admission", "science-i-6-units", "6 units Science I Course List", "Complete 6 units from the Science I Course List.", [], "advisor", 0, 6, 3, "", "This tool cannot enumerate the full Science I list yet; verify with the official calendar.", 7),
    ("level-ii", "level-ii-modern-lab", "PHYSICS 2C03 and 2P03", "Modern Physics and Introductory Laboratory are listed in Level II.", ["PHYSICS2C03", "PHYSICS2P03"], "all", 2, 6, 3, "", "", 1),
    ("level-ii", "level-ii-computing", "Scientific Computing", "Complete DATASCI 2G03 or PHYSICS 2G03.", ["DATASCI2G03", "PHYSICS2G03"], "units", 0, 3, 3, "", "", 2),
    ("level-ii", "level-ii-diffeq", "MATH 2C03", "Complete Introduction to Differential Equations.", ["MATH2C03"], "units", 0, 3, 3, "", "", 3),
    ("level-ii", "level-ii-vector-calc", "Multivariable/vector calculus option", "Complete MATH 2MC3, MATH 2X03, or MATH 2XA3.", ["MATH2MC3", "MATH2X03", "MATH2XA3"], "units", 0, 3, 3, "", "", 4),
    ("level-ii", "level-ii-biophys", "BIOPHYS 2S03", "Complete Explorations in Medical and Biological Physics.", ["BIOPHYS2S03"], "units", 0, 3, 3, "", "", 5),
    ("level-ii", "level-ii-biochem", "Biochemistry option", "Complete one course from the official biochemistry group in Level II.", ["BIOCHEM2B03", "BIOCHEM2BB3", "BIOCHEM2EE3", "BIOCHEM3G03"], "units", 0, 3, 3, "", "Program notes recommend BIOCHEM 2EE3 and 3G03 for the full biochemistry sequence.", 6),
    ("level-ii", "level-ii-missing-level-i", "BIOLOGY/CHEM/MATH admission-note courses", "Complete BIOLOGY 1A03, CHEM 1AA3, and MATH 1B03/MATH 1ZC3 by end of Level II if not completed in Level I.", ["BIOLOGY1A03", "CHEM1AA3", "MATH1B03", "MATH1ZC3"], "advisor", 0, 0, 3, "", "Use this as an advisor-check item because the exact obligation depends on Level I choices.", 7),
    ("level-ii", "level-ii-anatomy", "Anatomy/physiology by graduation", "KINESIOL 2X03 or 2Y03 is required by graduation and encouraged in Level II or III.", ["KINESIOL2X03", "KINESIOL2Y03"], "units", 0, 3, 3, "", "", 8),
    ("level-iii", "level-iii-core", "Level III physics/math/biophys/medphys core", "Complete PHYSICS 2B03, PHYSICS 3K03, MATH 3C03, BIOPHYS 3S03, and MEDPHYS 4B03.", ["PHYSICS2B03", "PHYSICS3K03", "MATH3C03", "BIOPHYS3S03", "MEDPHYS4B03"], "all", 5, 15, 3, "", "", 1),
    ("level-iii", "level-iii-biochem-second", "Second biochemistry course", "Complete another course from the official biochemistry group.", ["BIOCHEM2B03", "BIOCHEM2BB3", "BIOCHEM2EE3", "BIOCHEM3G03"], "units", 0, 6, 3, "", "Checker counts total units from the group across the full plan.", 2),
    ("level-iii", "level-iii-focus-3-units", "3 units from Course Lists A/B/C", "Complete at least 3 units from one of the official focus lists.", ["CHEM3RC3", "MEDPHYS3C03", "MEDPHYS4D03", "MEDPHYS4F03", "MEDPHYS4I03", "MEDPHYS4RB3", "MEDPHYS4U03", "PHYSICS4E03", "PHYSICS4P06", "BIOCHEM2L06", "BIOCHEM3BP3", "BIOCHEM3D03", "BIOCHEM3MI3", "BIOCHEM3Z03", "BIOLOGY2B03", "BIOPHYS3D03", "BIOPHYS3G03", "BIOPHYS4P06", "PHYSICS2BB3", "PHYSICS3D03", "PHYSICS3N04", "PHYSICS3P03", "PHYSICS4F03", "PHYSICS4G03", "PHYSICS4K03"], "units", 0, 3, 3, "", "", 3),
    ("level-iv", "level-iv-core", "Level IV required core", "Complete BIOPHYS 4S03, MEDPHYS 4RA3, MEDPHYS 4T03, and PHYSICS 3MM3.", ["BIOPHYS4S03", "MEDPHYS4RA3", "MEDPHYS4T03", "PHYSICS3MM3"], "all", 4, 12, 3, "", "", 1),
    ("level-iv", "level-iv-focus-9-units", "9 units from Course Lists A/B/C", "Complete 9 upper-year units from the official focus lists.", ["CHEM3RC3", "KINESIOL2XX3", "KINESIOL2YY3", "MEDPHYS3C03", "MEDPHYS4D03", "MEDPHYS4F03", "MEDPHYS4I03", "MEDPHYS4RB3", "MEDPHYS4U03", "MEDPHYS4Y06", "PHYSICS4E03", "PHYSICS4P06", "BIOCHEM2L06", "BIOCHEM3BP3", "BIOCHEM3D03", "BIOCHEM3MI3", "BIOCHEM3Z03", "BIOCHEM4E03", "BIOCHEM4H03", "BIOCHEM4M03", "BIOCHEM4N03", "BIOCHEM4Q03", "BIOLOGY2B03", "BIOPHYS3D03", "BIOPHYS3G03", "BIOPHYS4P06", "PHYSICS2BB3", "PHYSICS3D03", "PHYSICS3N04", "PHYSICS3P03", "PHYSICS4F03", "PHYSICS4G03", "PHYSICS4K03"], "units", 0, 9, 3, "", "Students targeting one focus should plan 12 units from that list across upper years.", 2),
    ("track-medical-physics", "track-a-12-units", "Course List A 12-unit recommendation", "Recommended for medical physics or health physics, especially postgraduate preparation.", ["CHEM3RC3", "KINESIOL2XX3", "KINESIOL2YY3", "MEDPHYS3C03", "MEDPHYS4D03", "MEDPHYS4F03", "MEDPHYS4I03", "MEDPHYS4RB3", "MEDPHYS4U03", "MEDPHYS4Y06", "PHYSICS4E03", "PHYSICS4P06"], "units", 0, 12, 3, "Medical Physics", "These courses contribute to CAMPEP-relevant undergraduate knowledge objectives according to the calendar note.", 1),
    ("track-biological-physics", "track-b-12-units", "Course List B 12-unit recommendation", "Recommended for students interested in biochemistry and biological physics/postgraduate paths.", ["BIOCHEM2L06", "BIOCHEM3BP3", "BIOCHEM3D03", "BIOCHEM3MI3", "BIOCHEM3Z03", "BIOCHEM4E03", "BIOCHEM4H03", "BIOCHEM4M03", "BIOCHEM4N03", "BIOCHEM4Q03", "BIOLOGY2B03", "BIOPHYS3D03", "BIOPHYS3G03"], "units", 0, 12, 3, "Biological Physics", "", 1),
    ("track-soft-matter", "track-c-12-units", "Course List C 12-unit recommendation", "Recommended for students interested in physics and soft matter physics/postgraduate paths.", ["BIOPHYS4P06", "PHYSICS2BB3", "PHYSICS3D03", "PHYSICS3N04", "PHYSICS3P03", "PHYSICS4F03", "PHYSICS4G03", "PHYSICS4K03"], "units", 0, 12, 3, "Soft Matter", "", 1),
]


RESOURCES = [
    ("2025-2026 Undergraduate Calendar", "Official", OFFICIAL_LINKS["calendar"], "Canonical requirements for Honours Medical and Biological Physics.", True),
    ("MAP Honours Medical and Biological Physics", "Official", OFFICIAL_LINKS["map"], "Plain program overview, admission buckets, typical second-year courses, and career examples.", True),
    ("Physics undergraduate programs", "Official", OFFICIAL_LINKS["physics_programs"], "Department overview and co-op note.", True),
    ("Physics course outlines", "Official", OFFICIAL_LINKS["course_outlines"], "Current Simple Syllabus and archived Physics outlines.", True),
    ("Upper-year research projects", "Official", OFFICIAL_LINKS["research_projects"], "Research project, literature review, teaching placement, and senior project details.", True),
    ("Medical Physics - RadGrad", "Official", OFFICIAL_LINKS["radgrad_medphys"], "Professional medical physics and accreditation context.", True),
    ("CAMPEP graduate program", "Official", OFFICIAL_LINKS["campep"], "McMaster CAMPEP-accredited MSc and PhD streams and core graduate courses.", True),
    ("CAMPEP residency applicant information", "Official", OFFICIAL_LINKS["campep_residency"], "Residency applicant expectations and physics-foundation guidance.", True),
    ("CCPM certification", "Official", OFFICIAL_LINKS["ccpm"], "Canadian clinical medical physics certification context.", True),
    ("Ontario Medical Physics Residency Program", "Official", OFFICIAL_LINKS["ontario_residency"], "Ontario medical physics residency pathway information.", True),
    ("McMaster USRA", "Official", OFFICIAL_LINKS["mcmaster_usra"], "McMaster administration of undergraduate student research awards.", True),
    ("NSERC USRA", "Official", OFFICIAL_LINKS["nserc_usra"], "National undergraduate student research award eligibility and process.", True),
    ("Medical Radiation Sciences", "Official", OFFICIAL_LINKS["mrsc"], "MRSc specializations and McMaster-Mohawk credential structure.", True),
    ("MRSc FAQ", "Official", OFFICIAL_LINKS["mrsc_faq"], "MRSc transfer, specialization, clinical placement, and certification notes.", True),
    ("Science co-op programs", "Official", OFFICIAL_LINKS["science_coop"], "Science co-op program overview and employer-facing descriptions.", True),
    ("Science co-op prospective students", "Official", OFFICIAL_LINKS["science_coop_prospective"], "Co-op entry timing and preparation notes for Science students.", True),
    ("Science co-op current students", "Official", OFFICIAL_LINKS["science_coop_current"], "Current co-op student resources and work-term expectations.", True),
    ("Health Canada Radiation Protection Bureau", "Official", OFFICIAL_LINKS["health_canada_rpb"], "Radiation protection, dose registry, calibration, and policy context.", True),
    ("Clinical medical physics roadmap", "Careers", "/guide/clinical-medical-physics-roadmap", "Clinical medical physics pathway from undergrad to graduate training and certification.", False),
    ("Health physics guide", "Careers", "/guide/health-physics-radiation-protection", "Radiation protection and nuclear/radiation safety pathway.", False),
    ("Imaging AI portfolio guide", "Careers", "/guide/medical-imaging-ai-portfolio", "Portfolio and skill-building guide for imaging, AI, and data science.", False),
    ("NSERC and summer research guide", "Research", "/guide/nserc-usra-and-summer-research", "Supervisor outreach, USRA strategy, and summer research planning.", False),
    ("Thesis and senior project guide", "Research", "/guide/thesis-and-senior-project-guide", "Supervisor fit, project scoping, and final-year research outputs.", False),
    ("Course review guidelines", "Community", "/guide/course-review-guidelines", "What student reviews can and cannot include.", False),
    ("Ask an upper-year", "Community", "/community/ask", "Submit a moderated question to the Isocentre community queue.", False),
    ("Mentor directory", "Community", "/community/mentors", "Opt-in public directory of students and alumni.", False),
]


def seed_database(session):
    prune_stale(session)
    upsert_pages(session)
    upsert_courses(session)
    upsert_rules(session)
    upsert_resources(session)


def prune_stale(session):
    current_rule_codes = {item[1] for item in REQUIREMENT_RULES}
    RequirementRule.query.filter(~RequirementRule.code.in_(current_rule_codes)).delete(synchronize_session=False)


def upsert_pages(session):
    for data in PAGES:
        page = Page.query.filter_by(slug=data["slug"]).first() or Page(slug=data["slug"])
        data = {**data, "body_html": md(data["body_markdown"]), "last_verified_at": datetime.now(timezone.utc)}
        for key, value in data.items():
            setattr(page, key, value)
        session.add(page)


def upsert_courses(session):
    for data in COURSES:
        course = Course.query.filter_by(code=data["code"]).first() or Course(code=data["code"])
        for key, value in data.items():
            setattr(course, key, value)
        session.add(course)


def upsert_rules(session):
    for item in REQUIREMENT_RULES:
        requirement_set, code, label, description, options, rule_type, required_count, units_required, option_units, track, note, order = item
        rule = RequirementRule.query.filter_by(code=code).first() or RequirementRule(code=code)
        rule.requirement_set = requirement_set
        rule.label = label
        rule.description = description
        rule.course_options = [[course] for course in options]
        rule.rule_type = rule_type
        rule.required_count = required_count
        rule.units_required = units_required
        rule.option_units = option_units
        rule.track = track
        rule.advisory_note = note
        rule.sort_order = order
        session.add(rule)


def upsert_resources(session):
    for title, category, url, description, is_official in RESOURCES:
        link = ResourceLink.query.filter_by(title=title, url=url).first() or ResourceLink(title=title, url=url)
        link.category = category
        link.description = description
        link.is_official = is_official
        session.add(link)
