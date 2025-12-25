# CLAUDE.md

## **Context Retrieval Protocol**
Before performing **any implementation, coding, architectural decision, or task execution**, the system **MUST first retrieve and load the context** for working with **asyncpg and FastAPI**.

This file defines the strict rules that Claude (or any assistant/service using this repo) must follow.

---

## **1. Mandatory Context Step**
Before doing anything, the assistant must:

1. **Search for and load `context7`**, which contains the authoritative references for:
   - asyncpg usage and connection pooling patterns
   - Direct SQL query patterns with asyncpg
   - FastAPI integration patterns
   - Database helper function patterns
   - Connection pool management
   - Transaction handling with asyncpg
2. The assistant **must not** proceed with any task **until context7 is fully loaded and understood**.

**Important**: This project uses **asyncpg directly** (no ORM, no SQLAlchemy). All database access is through direct SQL queries using asyncpg's connection pool.

If `context7` is not found:
- The assistant must **STOP**,
- Ask the user: *"Please provide context7, or point me to the file containing the asyncpg + FastAPI context."*

---

## **2. Implementation Safety Rules**
After loading `context7`, the assistant must follow these rules:

### **Rule A — No Assumptions**
The assistant must not invent:
- Database helper functions or SQL queries
- Connection pool configurations
- Router patterns
- Dependency injection logic
- Database schema structures

**Critical**: Do NOT use SQLAlchemy or any ORM. The project uses asyncpg with direct SQL queries only.

Unless explicitly provided in `context7`.

### **Rule B — Consistency Enforcement**
All implementations must be consistent with the architecture defined in `context7`.
If the user's request contradicts the context, the assistant must warn them.

### **Rule C — Ask Before Acting**
If any information is missing—such as model definitions or session setup—the assistant must ask the user first.

---

## **3. Task Execution Flow**
Every task must follow this sequence:

### **Step 1 — Retrieve context7**
- Load and parse context7.
- Summarize key architectural patterns.

### **Step 2 — Validate User Request**
- Check if the request fits the defined architecture.
- If unclear → request clarification.

### **Step 3 — Action**
- Implement only after validation.
- Ensure code follows asyncpg + FastAPI best practices defined in context7.
- Use direct SQL queries with asyncpg - no ORM layer.

---

## **4. Examples of Allowed and Forbidden Behavior**

### **Allowed**
- "Context7 loaded. The connection pool pattern uses `asyncpg.create_pool()`. Proceeding to implement the database helper function."
- "Using asyncpg connection pool from `get_db_pool()` for direct SQL queries."

### **Forbidden**
- "Here is the implementation…" (without loading context7 first)
- Using SQLAlchemy or any ORM
- Guessing database schema or SQL query patterns
- Creating connection pool configs not specified in context7
- Using ORM models instead of direct SQL with asyncpg

---

## **5. Goal of This Document**
This document forces discipline: **always load the correct architectural context first** before coding anything.

This ensures correctness, consistency, and eliminates accidental architecture drift.

---

If you'd like, I can also generate:
- `CONTEXT7.md`
- A template for SQLAlchemy + FastAPI project structure
- Auto-check scripts to enforce this rule


---

## **6. Steering Update Requirements (For Cursor, Claude, and Any AI Tool)**
To maintain long-term project clarity and prevent architectural drift, **any AI system (Cursor, Claude, or others)** that introduces changes to workflow, tooling, or implementation patterns must follow this rule:

### **Rule D — Mandatory Steering Synchronization**
If the assistant applies or suggests ANY change that affects:
- Project architecture
- Database access patterns (asyncpg vs ORM)
- FastAPI integration style
- Connection pool structure
- Dependency injection method
- Code generation conventions
- File organization
- Automated context retrieval
- MCP tool usage

Then the assistant **MUST update this `CLAUDE.md` steering document accordingly**, ensuring it remains: 
- Accurate
- Current
- Reflective of new workflows or constraints

### **Rule E — No Silent Breaking Changes**
Any AI proposing changes MUST:
1. Detect and acknowledge the breaking change
2. Update `CLAUDE.md` to reflect the new rule or alteration
3. Explain the update in a summary
4. Ask for confirmation **if the change modifies the project architecture**

### **Rule F — Documentation-First Discipline**
Before executing any code-level changes that alter existing behavior, the assistant must:
- Update documentation **first**
- Then proceed with implementation

This ensures that the codebase remains well-documented, understandable, and consistent without requiring full code scanning by contributors.

---

## **7. Purpose of Steering Update Requirements**
These rules guarantee:
- Long-term maintainability
- Architectural consistency
- Traceability of design decisions
- Reduced cognitive load for contributors
- An always up-to-date project spec without reading the entire codebase

This makes the project self-explanatory, even for new developers or future AI agents.

---

## **8. Virtual Environment Activation Requirements**
Before running **any Python script, command, or test**, the assistant **MUST activate the virtual environment** using the following commands:

### **Rule G — Mandatory Virtualenv Activation**
The assistant must execute these commands in sequence before running any Python-related operations:

1. **Set pyenv shell environment:**
   ```bash
   pyenv shell letsplay
   ```

2. **Activate the virtual environment:**
   ```bash
   pyenv activate letsplay
   ```

### **Rule H — Environment Verification**
After activation, the assistant should verify the environment is active by:
- Checking that the Python interpreter path includes the virtualenv
- Ensuring dependencies are accessible
- Confirming the correct Python version is in use

### **Rule I — Consistent Environment Usage**
All Python operations must be performed within the activated virtualenv:
- Running scripts
- Installing packages
- Running tests
- Executing migrations
- Starting the application server

**Critical**: Never run Python commands without first activating the virtualenv as specified above.

---
