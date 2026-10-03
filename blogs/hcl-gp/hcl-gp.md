---
title: "Learning from Success: How Reusable Policies Drive State-of-the-Art Performance on AppWorld"
subtitle: "HCL-GP combines generalized planning, hierarchical decomposition, and execution-grounded learning to help LLM agents accumulate and reuse procedural knowledge."
author: "Michael Katz, Shirin Sohrabi, Haritha Ananthakrishnan, Harsha Kokel, Kavitha Srinivas"
date: 2026-05-21
slug: "learning-reusable-policies-appworld"
summary: "HCL-GP reached 97.8% Scenario Goal Completion on the AppWorld Challenge benchmark by learning, validating, generalizing, and reusing executable policy components."
tags:
  - AI agents
  - AI planning
  - generalized planning
  - hierarchical planning
  - LLM agents
  - AppWorld
---

# Learning from Success: How Reusable Policies Drive State-of-the-Art Performance on AppWorld

Today’s AI agents can execute increasingly complex digital tasks. They can call APIs, inspect results, generate code, and correct failures. Yet most agents still approach every new task as if they had never encountered anything similar before.

Our recent work asks a simple question: **Can an agent learn reusable ways of solving problems from its own successful executions?**

The answer appears to be yes. Our approach, **Hierarchical Component Learning for Generalized Policies**, or **HCL-GP**, achieves **97.8% Scenario Goal Completion on the AppWorld Challenge benchmark**.

The Challenge set is designed to test robust generalization on difficult, multi-step tasks. It includes applications, specifically Gmail and Amazon, that do not appear in the training set. The agent must generate executable code, coordinate API calls, process intermediate results, and satisfy the requested goal without causing unintended changes.

**Scenario Goal Completion**, or **SGC**, is AppWorld’s stricter evaluation metric. A scenario counts as successful only if the agent solves every task within it. One failed task causes the entire scenario to be counted as unsuccessful. A 97.8% SGC score therefore reflects consistent end-to-end performance across complete scenarios, rather than a high average that may conceal individual failures.

The result suggests that combining modern language models with ideas from AI planning can produce agents that are not only capable, but also able to accumulate and reuse procedural knowledge.

## The problem with solving every task from scratch

[AppWorld](https://appworld.dev/appworld/) is a benchmark for interactive coding agents. It provides a simulated digital world with multiple applications and hundreds of APIs. Agents receive natural-language tasks and must generate and execute code that interacts with those applications. Evaluation is programmatic: it checks whether the intended result was achieved and whether the agent introduced collateral changes.

Many tasks share important structure. An agent may repeatedly need to authenticate with an application, retrieve and filter records, identify an entity, or perform a transaction. The application, parameters, and final objective may differ, but parts of the underlying procedure remain similar.

Most agents do not explicitly capture this similarity. They synthesize a new solution for each task, repeatedly rediscovering workflows they have already executed successfully. This consumes inference budget and creates additional opportunities for failure.

HCL-GP instead treats successful executions as experience from which reusable procedural knowledge can be learned.

## From individual tasks to generalized policies

The first idea behind HCL-GP comes from **generalized planning**.

Rather than generating a separate plan for every task, the system identifies the common structure across a group of related tasks and synthesizes a parameterized policy. Task-specific details, such as names, amounts, dates, or applications, become parameters of that policy.

For example, several tasks may require finding every item satisfying a condition and applying an action to each one. The specific items and action vary, but the control structure is shared. A generalized policy represents this common procedure once and instantiates it for each task.

The system first analyzes related tasks to determine:

- the high-level workflow they share;
- the parameters that vary among them; and
- the concrete parameter values required for each task.

It then generates an executable policy, instantiates it for the individual tasks, and runs the resulting plans in AppWorld. If validation fails, execution traces and error messages are used to debug the policy.

This validation loop is important. The policies are not merely plausible descriptions of how a task might be solved. They are executable programs tested against the actual environment.

## Learning reusable skills from successful policies

Generalizing within one group of tasks is only part of the story. HCL-GP also learns across groups of tasks.

After a policy succeeds, the system analyzes its code and extracts coherent pieces of reusable logic. These components, which we call **skills**, may implement patterns such as authentication, retrieving paginated records, filtering results, looking up an entity, or coordinating calls across applications.

The original policy is rewritten to use the extracted skills and then executed again. A skill is accepted only if the revised policy continues to pass the original task tests.

As more tasks are solved, the skill repository grows. Similar skills are clustered, generalized, and deduplicated. For example, separate skills for logging in to different applications may be consolidated into a single parameterized login skill. The affected policies are validated again before the generalized skill is added to the repository.

This creates a continuous learning cycle:

1. **Generate** a policy for a family of tasks.
2. **Validate and debug** it through execution.
3. **Decompose** the successful policy into reusable skills.
4. **Generalize and deduplicate** related skills.
5. **Retrieve and compose** those skills when solving future tasks.

Over time, the system builds a library of executable, validated procedural knowledge.

## Why reuse matters

The most revealing result is not only the final score, but the difference between solving with and without reusable skills.

Using Claude Sonnet 4.6, generalized planning without skill reuse achieved **82.0% SGC on the Challenge set**. Adding hierarchical skill learning and reuse increased the result to **97.8%**, an improvement of **15.8 percentage points**.

The effect was even more pronounced with the open-source GPT-OSS 120B model. Without reuse, the generalized-planning baseline achieved **0.7% Challenge SGC**. With the same dynamic skill-learning architecture, it reached **41.0% Challenge SGC**. On the normal set, HCL-GP with GPT-OSS 120B reached **62.5% SGC**, compared with zero for the corresponding baseline.

These results indicate that the surrounding agent architecture can substantially change what a model is able to accomplish. A stronger foundation model helps, but the way an agent organizes, validates, and reuses experience can be equally consequential.

HCL-GP also achieved its Challenge result using Claude Sonnet 4.6 while outperforming systems based on larger models, achieving a **97.8% Challenge SGC score**.

## Bringing AI planning ideas into modern agents

HCL-GP draws on two established areas of AI planning.

**Generalized planning** focuses on policies that solve collections of related problems rather than individual instances. **Hierarchical planning** represents complex behavior through reusable decompositions and subtasks.

In classical planning systems, these ideas often rely on explicit symbolic models of states, actions, and transitions. HCL-GP applies similar principles in a setting where tasks are expressed in natural language and policies are represented as executable code. The hierarchy is not manually specified. It is induced from successful executions, generalized across tasks, and grounded through validation.

This combination provides several useful properties:

- **Generalization:** One parameterized policy can solve multiple related tasks.
- **Compositionality:** New policies can be assembled from previously learned skills.
- **Grounding:** Policies and skills are validated through execution.
- **Continuous improvement:** Each successful policy can expand the system’s capabilities.
- **Model leverage:** Reuse can make less capable models substantially more effective.

The broader implication is that agent learning need not mean updating model weights. Agents can also learn by constructing, validating, and maintaining a structured library of reusable behavior.

## Future directions

HCL-GP shows that agents can improve by extracting and reusing procedural knowledge from successful executions. It also opens several directions for further research.

### Discovering task families rather than assuming them

The current approach assumes that tasks are already partitioned into scenarios. This provides a useful signal about which tasks are likely to share a generalized policy. In less structured settings, that partition may not be available.

The agent would then need to discover the latent task families itself: determining which tasks share a common solution structure, when superficially different tasks can be captured by one generalized policy, and when apparently similar tasks require distinct policies. This turns policy learning into a joint problem of **task clustering, abstraction discovery, and policy synthesis**.

Ideally, the partition would not be fixed in advance. It could evolve as the agent acquires experience, with task families split, merged, or organized hierarchically as new structural similarities are discovered.

### Learning from failures

The current approach learns primarily from successful policies. Future systems could also learn systematically from failures by identifying recurring failure modes, recording conditions under which a skill should not be applied, and learning recovery procedures. The skill repository could then represent both effective behavior and known limits on that behavior.

### Managing the skill lifecycle

As an agent learns continuously, its repository may accumulate overlapping, obsolete, or overly specialized skills. Maintaining such a library requires mechanisms for consolidation, versioning, dependency tracking, and revalidation when applications or APIs change.

### Representing when a skill applies

Semantic retrieval can identify skills that appear relevant, but similarity alone does not guarantee that a skill is valid in the current context. Explicit preconditions, effects, invariants, or learned applicability models could make composition more reliable and reduce unnecessary execution and repair.

### Learning richer hierarchical structures

The approach could be extended from reusing individual skills to learning richer hierarchical structures. Instead of retrieving a flat collection of components, an agent could learn alternative decompositions, select among them based on the current state, and adapt a partially applicable policy when the environment differs from prior experience.

### Moving beyond controlled benchmarks

Real applications evolve, expose incomplete information, produce nondeterministic outcomes, and may require interaction with users. Extending execution-grounded skill learning to these settings will require stronger mechanisms for monitoring, verification, safe execution, and adaptation.

Together, these directions point toward agents that do more than solve isolated tasks. The longer-term goal is an agent that can discover structure in an initially unorganized stream of experience, use that structure to build generalized policies, and continuously maintain a validated body of reusable procedural knowledge.

## Toward agents that accumulate experience

Current LLM agents are often effective problem solvers, but weak cumulative learners. They can solve a task and then discard most of what the solution taught them.

HCL-GP demonstrates an alternative. Agents can transform successful behavior into generalized policies, decompose those policies into reusable skills, validate the resulting abstractions, and apply them compositionally to new problems. Its strong results on the AppWorld Challenge benchmark provide clear evidence that this combination of generalization, hierarchy, and reuse can improve end-to-end agent reliability.

More broadly, the work illustrates how ideas developed in AI planning can complement advances in foundation models. Building more capable agents may require not only models that reason better in the moment, but systems that can retain, organize, validate, and reuse what they have already learned.

The paper, **“Learning and Reusing Policy Decompositions for Hierarchical Generalized Planning with LLM Agents,”** is joint work by Shirin Sohrabi, Haritha Ananthakrishnan, Harsha Kokel, Kavitha Srinivas, and Michael Katz at IBM.

**[Read the paper](https://arxiv.org/abs/2605.06957)**
