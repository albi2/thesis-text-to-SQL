# UMB(Update Memory Bank) Guidelines
## Purpose

Update the memory bank documents based on the strategy below.

## Memory Bank Documents

1. decisionLog.md - Records architectural and implementation decisions, including the context, decision, rationale, and implementation details. Template
   ```
      # Decision Log

      This file records architectural and implementation decisions using a list format.
      YYYY-MM-DD HH:MM:SS - Log of updates made.

      *
      
      ## Decision

      *
      
      ## Rationale 

      *

      ## Implementation Details

      *
   ```
2. productContext.md	- Provides a high-level overview of the project, including its goals, features, and overall architecture. Template:
   ```
      # Product Context
      
      This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
      YYYY-MM-DD HH:MM:SS - Log of updates made will be appended as footnotes to the end of this file.
      
      *

      ## Project Goal

      *   

      ## Key Features

      *   

      ## Overall Architecture

      *   
   ```
3. systemPatterns.md	- Documents recurring patterns and standards used in the project (coding patterns, architectural patterns, etc). Template:
   ```
      # System Patterns 

      This file documents recurring patterns and standards used in the project.
      YYYY-MM-DD HH:MM:SS - Log of updates made.

      *

      ## Coding Patterns

      *   

      ## Architectural Patterns

      *   
   ```

## Strategy
The YAML below explains when to modify each file in the memory bank and how it is triggered.
```
memory_bank_updates:
  decisionLog.md:
    trigger: "When a significant architectural decision is made (new component, data flow change, technology choice, etc.). Use your judgment to determine significance."
    action: |
      <thinking>
      I need to update decisionLog.md with a decision, the rationale, and any implications.
      Use insert_content to *append* new information. Never overwrite existing entries. Always include a timestamp.
      </thinking>
    format: |
      "[YYYY-MM-DD HH:MM:SS] - [Summary of Change/Focus/Issue]"
  productContext.md:
    trigger: "When the high-level project description, goals, features, or overall architecture changes significantly. Use your judgment to determine significance."
    action: |
      <thinking>
      A fundamental change has occurred which warrants an update to productContext.md.
      Use insert_content to *append* new information or use apply_diff to modify existing entries if necessary. Timestamp and summary of change will be appended as footnotes to the end of the file.
      </thinking>
    format: "(Optional)[YYYY-MM-DD HH:MM:SS] - [Summary of Change]"
  systemPatterns.md:
    trigger: "When new architectural patterns are introduced or existing ones are modified. Use your judgement."
    action: |
      <thinking>
      I need to update systemPatterns.md with a brief summary and time stamp.
      Use insert_content to *append* new patterns or use apply_diff to modify existing entries if warranted. Always include a timestamp.
      </thinking>
    format: "[YYYY-MM-DD HH:MM:SS] - [Description of Pattern/Change]"

update_memory_bank_rules:
  core_update_process: |
      1. Current Session Review:
          - Analyze complete chat history
          - Extract most relevant information / updates
      2. Map Updates To Memory Files:
          - Determine to which file should each of the updates in the session should be added.
          - Determine which of the updates are too specific and not necessary to be added at all.
      3. Memory Bank Synchronization:
          - Update all affected *.md files
  task_focus: "During a UMB update, focus on capturing any clarifications, questions answered, or context provided *during the chat session*. Make sure these are *major points* such as important classes, designs or changes in business/architecture. This information should be added to the appropriate Memory Bank files (likely `systemPatterns.md` or `decisionLog.md`).  *Do not* attempt to summarize the entire project or perform actions outside the scope of the current chat. "
  rules: 
    general: |
      1. Do *NOT* be super specific on what you write in the memory-bank decisionLog.md. For example avoid things like: "Used constants for better readibility or used context factory to do Y." Here we want to store major decision regarding code structure or architecture.
      2. As a rule of thumb, if some decision / logic can be understood by reading the specific code class or function there is no need to add it to the .md files. We just need to store that this class / method / component exist.
      3. Always use judgment to determine if a change need to be recorded at all and if you need to write a lot or very little about it so that you know how to understand it in the future. Context should be kept minimal but also big enough so that its easily understood by any coding agent.
      4. Do not use the same writing technique on all files. 
    decisionLog.md: |
      1. Some things such as use constants, or use factory pattern  or use builder pattern belong in the systemPatterns.md and not in the decisionLog.md. Always critically decide where a change needs to be documented. 
      2. decisionLog.md requires enough words to express the architecture but also we can use mermaid diagrams, folder structures, class names , component names, abstractions and interfaces etc just to express high level ideas.
      3. You do not need to add an entry for each of the sections of the file. Sometimes a decision entry and a rationale is enough without implementation details. Use your judgment by determine if the implementation details might be relevant or not in the future.
    productContext.md: |
      1. productContext.md by default requires more words as explanation is necessary to understand the product.
    systemPatterns.md: |
      1. systemPatterns.md needs to be more concise and provide examples of code where possible however for things like using a specific design pattern, keeping constants classes there is no need to be super detailed. 
      E.g Architectural Pattern "Use factory design pattern for major classes in code or for strategy classes and give some method call example". Again use your judgment here on whether it needs to be a long or short one and if the code example needs to be a really short method call for example or something longer.
      E.g Coding Pattern "Keep constant literals on a separate file. Short coding example"
      2. Keep the patterns general and not tied to specific classes on the code. They should serve as guidelines on how to write code not explain what pattern was followed on a specific piece of code.
```