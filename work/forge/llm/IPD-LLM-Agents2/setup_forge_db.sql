/******************************************************************************
 * Practicum I - FORGE IPD2 Schema Setup
 * Persistent Storage Schema for Iterated Prisoner's Dilemma with LLM Agents
 *
 * Emily D. Carpenter
 * Anderson College of Business and Computing, Regis University
 * MSDS 692/S41: Data Science Practicum I
 * Dr. Douglas Hart, Dr. Kellen Sorauf
 * February 2026
 ******************************************************************************/

CREATE SCHEMA ipd2;

/***************************** Create the Tables ******************************/
CREATE TABLE ipd2.results (
  results_id                    SERIAL PRIMARY KEY
  ,filename                      VARCHAR(128) UNIQUE
  ,timestamp                    TIMESTAMPTZ UNIQUE
  ,hostname                     VARCHAR(64)
  ,username                     VARCHAR(64)
  ,elapsed_seconds              DOUBLE PRECISION
  ,cfg_num_episodes             SMALLINT
  ,cfg_round_per_episode        SMALLINT
  ,cfg_total_rounds             INTEGER
  ,cfg_history_window_size      SMALLINT
  ,cfg_temperature              REAL
  ,cfg_reset_between_episodes   BOOL
  ,cfg_reflection_type          VARCHAR(64)
  ,cfg_decision_token_limit     INTEGER
  ,cfg_reflection_token_limit   INTEGER
  ,cfg_http_timeout             SMALLINT
  ,cfg_force_decision_retries   SMALLINT
  ,system_prompt                TEXT
  ,reflection_template          TEXT
  ,raw_json                     JSONB
);

CREATE TABLE ipd2.llm_agents (
  results_id                INTEGER
  ,agent_idx                SMALLINT
  ,host                     VARCHAR(64)
  ,agent_model              VARCHAR(64)
  ,cfg_model                VARCHAR(64)
  ,total_score              SMALLINT
  ,total_cooperations       SMALLINT
  ,overall_cooperation_rate REAL

  ,PRIMARY KEY (results_id, agent_idx)
  ,FOREIGN KEY (results_id) REFERENCES ipd2.results(results_id)
);

CREATE TABLE ipd2.episodes (
  episode_id                SERIAL PRIMARY KEY
  ,results_id               INTEGER
  ,agent_idx                SMALLINT
  ,episode                  SMALLINT
  ,score                    SMALLINT
  ,cooperations             SMALLINT
  ,cooperation_rate         DOUBLE PRECISION
  ,reflection               TEXT

  ,FOREIGN KEY (results_id) REFERENCES ipd2.results(results_id)
  ,FOREIGN KEY (results_id, agent_idx) REFERENCES ipd2.llm_agents(results_id, agent_idx)
  ,UNIQUE (results_id, agent_idx, episode)
);

CREATE TABLE ipd2.rounds (
  episode_id                INTEGER
  ,round                    SMALLINT
  ,action                   VARCHAR(64)
  ,payoff                   SMALLINT
  ,ep_cumulative_score      SMALLINT
  ,reasoning                TEXT

  ,PRIMARY KEY (episode_id, round)
  ,FOREIGN KEY (episode_id) REFERENCES ipd2.episodes(episode_id)
);

/******************************** Grant Access ********************************/
GRANT USAGE ON SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205;

/* Grant full access to tables */
GRANT ALL ON ALL TABLES IN SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205;

/* Grant access to read and use SERIAL fields */
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205;
  
/**************************** Master Results View ****************************/
CREATE OR REPLACE VIEW ipd2.results_vw AS
SELECT
    r.*
    
    ,a.agent_idx
    ,a.host                         AS agent_host
    ,a.agent_model
    ,a.cfg_model
    ,a.total_score
    ,a.total_cooperations
    ,a.overall_cooperation_rate
    
    ,e.episode_id
    ,e.episode
    ,e.score                        AS episode_score
    ,e.cooperations                 AS episode_cooperations
    ,e.cooperation_rate             AS episode_cooperation_rate
    ,e.reflection
    
    ,rd.round
    ,rd.action
    ,rd.payoff
    ,rd.ep_cumulative_score
    ,rd.reasoning
    
FROM ipd2.results r
    JOIN ipd2.llm_agents a ON r.results_id = a.results_id
    JOIN ipd2.episodes e ON r.results_id = e.results_id AND a.agent_idx = e.agent_idx
    JOIN ipd2.rounds rd ON e.episode_id = rd.episode_id
    
ORDER BY
    r.timestamp
    ,a.agent_idx
    ,e.episode
    ,rd.round;