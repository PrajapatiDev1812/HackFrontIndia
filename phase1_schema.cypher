// ============================================================
// Aura GraphRAG — phase1_schema.cypher
// Run this ONCE against Neo4j after first startup.
// Safe to re-run — all statements use IF NOT EXISTS.
// ============================================================


// ── SECTION 1: UNIQUENESS CONSTRAINTS ───────────────────────────────────────
// Each constraint also creates a backing index automatically.

CREATE CONSTRAINT repo_id_unique
  IF NOT EXISTS
  FOR (r:Repo)
  REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT pr_id_unique
  IF NOT EXISTS
  FOR (p:PR)
  REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT commit_sha_unique
  IF NOT EXISTS
  FOR (c:Commit)
  REQUIRE c.sha IS UNIQUE;

// File path is the natural unique key (repo-relative path)
CREATE CONSTRAINT file_path_unique
  IF NOT EXISTS
  FOR (f:File)
  REQUIRE f.path IS UNIQUE;

CREATE CONSTRAINT developer_login_unique
  IF NOT EXISTS
  FOR (d:Developer)
  REQUIRE d.login IS UNIQUE;

CREATE CONSTRAINT decision_id_unique
  IF NOT EXISTS
  FOR (dec:Decision)
  REQUIRE dec.id IS UNIQUE;

// Topic names are canonical (lowercase, e.g. "performance", "security")
CREATE CONSTRAINT topic_name_unique
  IF NOT EXISTS
  FOR (t:Topic)
  REQUIRE t.name IS UNIQUE;


// ── SECTION 2: PERFORMANCE INDEXES ──────────────────────────────────────────
// Created on frequently queried / filtered properties.

// PR state — used in implicit supersession queries (WHERE p.state = 'closed')
CREATE INDEX pr_state_idx
  IF NOT EXISTS
  FOR (p:PR)
  ON (p.state);

// PR timestamps — used for chronological ordering and range queries
CREATE INDEX pr_created_at_idx
  IF NOT EXISTS
  FOR (p:PR)
  ON (p.created_at);

CREATE INDEX pr_merged_at_idx
  IF NOT EXISTS
  FOR (p:PR)
  ON (p.merged_at);

// PR number — used in supersession detection (WHERE p.number = $pr_number)
CREATE INDEX pr_number_idx
  IF NOT EXISTS
  FOR (p:PR)
  ON (p.number);

// Decision type — used when filtering by category (api_design, security, etc.)
CREATE INDEX decision_type_idx
  IF NOT EXISTS
  FOR (d:Decision)
  ON (d.decision_type);

// Decision confidence — used when ranking/sorting by confidence score
CREATE INDEX decision_confidence_idx
  IF NOT EXISTS
  FOR (d:Decision)
  ON (d.confidence);

// File path (also covered by unique constraint, this is for CONTAINS lookups)
CREATE INDEX file_path_idx
  IF NOT EXISTS
  FOR (f:File)
  ON (f.path);

// File extension — useful for filtering by language (e.g. WHERE f.extension = 'py')
CREATE INDEX file_extension_idx
  IF NOT EXISTS
  FOR (f:File)
  ON (f.extension);


// ── SECTION 3: VERIFY ───────────────────────────────────────────────────────
// After running, verify with these two commands in Neo4j Browser:

// SHOW CONSTRAINTS;
// SHOW INDEXES;

// Expected: 7 constraints, 8+ indexes
