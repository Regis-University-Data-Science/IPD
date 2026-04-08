/******************************************************************************
 * Practicum II - FORGE IPD2 Schema Permissions Setup
 * Persistent Storage Schema for Iterated Prisoner's Dilemma with LLM Agents
 *
 * Emily D. Carpenter
 * Anderson College of Business and Computing, Regis University
 * MSDS 696/S71: Data Science Practicum II
 * Dr. Douglas Hart, Dr. Kellen Sorauf
 * March 2026
 *
 * Revision History:
 *  20260329: Initial creation of grants for containerized database.
 ******************************************************************************/

GRANT USAGE ON SCHEMA ipd2 TO PUBLIC;
GRANT ALL ON ALL TABLES IN SCHEMA ipd2 TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ipd2 TO PUBLIC;
