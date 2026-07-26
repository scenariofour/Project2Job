# Product North Star

## Product description

Project2Job is a role-backwards project career system for early-career AI PM candidates.

It starts from one real target JD, works out which of the user's projects is worth investigating, verifies what that project actually proves, and converts supported evidence into a company-specific application and interview pack.

## User problem

Candidates often build AI projects through tutorials, coding agents, or rapid prototyping. During development, the project can drift away from the capabilities the candidate originally wanted to demonstrate.

When a target JD appears, the candidate may not know:

- which of their projects is worth putting forward for this role
- which parts of that project matter for this role
- whether the project is strong enough to include
- which claims are defensible
- what should be changed before applying
- how the same project should appear in a resume and interview
- whether added complexity creates career evidence or only technical surface area

## Product job

Help the user turn one target JD and one of their real projects into a defensible
application for that specific company and track.

## User-facing promise

Give Project2Job one target JD, optionally a resume, and one selected real
project. It identifies the best project to investigate, verifies its evidence,
and produces a company-specific application and interview pack.

Before any project evidence is supplied it returns an Intake Result:

- what the role demands
- what is known about the company and track, each item with its source status
- which resume projects are candidates, and which one to investigate
- why that project, and what could make the recommendation wrong
- which claims still need verification
- what evidence to supply next

After the selected project's evidence is verified it returns an Application and
Interview Pack:

- the role capabilities the project currently supports
- the strongest evidence-grounded project highlights
- tailored resume bullets and a 30-second project introduction
- a company and track brief with an interview-loop hypothesis
- prioritized questions, grounded answer drafts, and likely follow-ups
- the highest-risk unsupported area
- one project action that would improve the application

Company and interview research is never project evidence. The two travel
separately and are labeled differently at every stage.

## Long-term product idea

The stateful Agent can become a personal Career Evidence OS that maintains:

- role standards
- project evidence profiles
- confirmed ownership
- project change history
- application-specific assets
- interview questions and feedback

The MVP proves only the first JD-to-application cycle and one update cycle.

## North-star behavior

The user uses a generated asset or changes the project because of Project2Job.

Examples:

- adopts a grounded resume bullet
- removes or narrows an unsupported claim
- completes the recommended project action
- improves an interview answer using source-backed evidence
- investigates the recommended project instead of the one they assumed
- reruns after updating the project
