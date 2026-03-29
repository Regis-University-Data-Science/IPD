/******************************************************************************
 * Practicum I - FORGE IPD2 Schema Setup
 * Persistent Storage Schema for Iterated Prisoner's Dilemma with LLM Agents
 *
 * Emily D. Carpenter
 * Anderson College of Business and Computing, Regis University
 * MSDS 692/S41: Data Science Practicum I
 * Dr. Douglas Hart, Dr. Kellen Sorauf
 * February 2026
 *
 * Revision History:
 *  20260316: Added "comment" field to ipd2.results; updated all SQL views
 *  20260329: Created separate GRANTS SQL script file.
 ******************************************************************************/

GRANT USAGE ON SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205, theandyman;

/* Grant full access to tables */
GRANT ALL ON ALL TABLES IN SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205, theandyman;

/* Grant access to read and use SERIAL fields */
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205, theandyman;
