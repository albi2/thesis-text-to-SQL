# Initialize Memory Bank Guidelines

## Purpose

Initialize the memory bank files to store the project's relevant decision-making and coding details.

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

The initialization strategy is provided in the YAML below.
```
initialization_strategy_steps:
  check_file_initialization: |
      1. Check if memory-bank folder exists in the root directory.
      2. If memory-bank does not exist go to if_no_memory_bank step.
      3. If memory-bank exists go to if_memory_bank_exists step.
  if_no_memory_bank: |
      1. Create memory bank folder using the templates for each file shown above. ALWAYS follow these templates when dealing with the memory bank.
      2. Read the contents of docs/planning/project_desc.md and update the relevant files from the memory bank. Most of the time only the productContext.md file will need to be updated.
      3. Read the contents of docs/coding/designPatterns.md and update the relevant files from the memory bank.
  if_memory_bank_exists: |
        **READ *ALL* MEMORY BANK FILES**
        Plan: Read all mandatory files sequentially.
        1. Read `productContext.md`
        3. Read `systemPatterns.md` 
        4. Read `decisionLog.md` 
```

