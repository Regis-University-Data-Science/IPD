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
  ,filename                     VARCHAR(128) UNIQUE
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
  ,FOREIGN KEY (results_id) 
        REFERENCES ipd2.results(results_id) ON DELETE CASCADE
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

  ,FOREIGN KEY (results_id) 
        REFERENCES ipd2.results(results_id) ON DELETE CASCADE

  ,FOREIGN KEY (results_id, agent_idx) 
        REFERENCES ipd2.llm_agents(results_id, agent_idx) ON DELETE CASCADE

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

  ,FOREIGN KEY (episode_id) 
        REFERENCES ipd2.episodes(episode_id) ON DELETE CASCADE
);

CREATE TABLE ipd2.research_log (
  log_id                    SERIAL PRIMARY KEY
  ,create_dttm              TIMESTAMPTZ
  ,log_dttm                 TIMESTAMPTZ
  ,username                 VARCHAR(64)
  ,subject                  VARCHAR(256)
  ,remarks                  TEXT
  ,tags                     TEXT[]
);

/******************************** Grant Access ********************************/
GRANT USAGE ON SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205, theandyman;

/* Grant full access to tables */
GRANT ALL ON ALL TABLES IN SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205, theandyman;

/* Grant access to read and use SERIAL fields */
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ipd2 
  TO techkgirl, dhart, ksorauf, priyankasaha205, theandyman;
  
 /********************************* SQL Views *********************************/
CREATE OR REPLACE VIEW ipd2.get_raw_data_vw AS
SELECT
    r.results_id
    ,r.username
    ,r.filename
    ,r.timestamp
    ,r.raw_json
FROM ipd2.results r
ORDER BY r.username, r.timestamp;
 
CREATE OR REPLACE VIEW ipd2.results_vw AS
SELECT
    -- Game set details and configuration
    r.results_id
    ,r.username
    ,r.filename
    ,r.timestamp
    ,r.hostname
    ,r.elapsed_seconds
    ,r.cfg_num_episodes
    ,r.cfg_round_per_episode
    ,r.cfg_total_rounds
    ,r.cfg_history_window_size
    ,r.cfg_temperature
    ,r.cfg_reset_between_episodes
    ,r.cfg_reflection_type
    ,r.cfg_decision_token_limit
    ,r.cfg_reflection_token_limit
    ,r.cfg_http_timeout
    ,r.cfg_force_decision_retries
    ,r.system_prompt
    ,r.reflection_template

    -- Agent details
    ,a.agent_idx
    ,a.host                         AS agent_host
    ,a.agent_model
    ,a.cfg_model
    ,a.total_score
    ,a.total_cooperations
    ,a.overall_cooperation_rate
    
    -- Episode and round details
    ,e.episode_id
    ,e.episode
    ,rd.round

    ,CONCAT('agent_',  a.agent_idx) AS agent
    ,rd.action
    ,rd.payoff
    ,rd.ep_cumulative_score
    ,rd.reasoning

    ,e.score                        AS episode_score
    ,e.cooperations                 AS ep_cooperations
    ,e.cooperation_rate             AS ep_coop_rate
    ,e.reflection                   AS ep_reflection
    
FROM 
    ipd2.results r
    
    JOIN ipd2.llm_agents a
        ON a.results_id = r.results_id
        
    JOIN ipd2.episodes e
        ON e.results_id = r.results_id
        AND e.agent_idx = a.agent_idx

    JOIN ipd2.rounds rd
        ON rd.episode_id = e.episode_id
        
ORDER BY
    r.timestamp
    ,a.agent_idx
    ,e.episode
    ,rd.round
;

CREATE OR REPLACE VIEW ipd2.experiment_summary_vw AS
SELECT
    -- Game set details and configuration
    r.results_id
    ,r.username
    ,r.filename
    ,r.timestamp
    ,r.hostname
    ,r.elapsed_seconds

    -- Agent 0
    ,a0.host                        AS agent_0_host
    ,a0.agent_model                 AS agent_0_model
    ,a0.total_score                 AS agent_0_total_score
    ,a0.total_cooperations          AS agent_0_total_cooperations
    ,a0.overall_cooperation_rate    AS agent_0_cooperation_rate
    
    -- Agent 1
    ,a1.host                        AS agent_1_host
    ,a1.agent_model                 AS agent_1_model
    ,a1.total_score                 AS agent_1_total_score
    ,a1.total_cooperations          AS agent_1_total_cooperations
    ,a1.overall_cooperation_rate    AS agent_1_cooperation_rate    

    ,r.cfg_num_episodes
    ,r.cfg_round_per_episode
    ,r.cfg_total_rounds
    ,r.cfg_history_window_size
    ,r.cfg_temperature
    ,r.cfg_reset_between_episodes
    ,r.cfg_reflection_type
    ,r.cfg_decision_token_limit
    ,r.cfg_reflection_token_limit
    ,r.cfg_http_timeout
    ,r.cfg_force_decision_retries
    ,r.system_prompt
    ,r.reflection_template

FROM 
    ipd2.results r

    JOIN ipd2.llm_agents a0 
        ON a0.results_id = r.results_id 
        and a0.agent_idx = 0

    JOIN ipd2.llm_agents a1 
        ON a1.results_id = r.results_id 
        and a1.agent_idx = 1

ORDER BY r.timestamp
;

CREATE OR REPLACE VIEW ipd2.episode_summary_vw AS
SELECT
    r.results_id
    ,r.username
    ,r.filename
    ,r.timestamp
    
    ,e0.episode

    ,e0.score                   AS agent_0_total_score
    ,e0.cooperations            AS agent_0_total_cooperations
    ,e0.cooperation_rate        AS agent_0_coop_rate
    ,e0.reflection              AS agent_0_reflection

    ,e1.score                   AS agent_1_total_score
    ,e1.cooperations            AS agent_1_total_cooperations
    ,e1.cooperation_rate        AS agent_1_coop_rate
    ,e1.reflection              AS agent_1_reflection

FROM 
    ipd2.results r

    JOIN ipd2.episodes e0
        on e0.results_id = r.results_id
        and e0.agent_idx = 0
    
    JOIN ipd2.episodes e1
        on e1.results_id = r.results_id
        and e1.agent_idx = 1
        and e1.episode = e0.episode

ORDER BY
    r.timestamp
    ,e0.episode
;

CREATE OR REPLACE VIEW ipd2.rounds_summary_vw AS
SELECT
    r.results_id
    ,r.username
    ,r.filename
    ,r.timestamp
    
    ,a0.episode
    ,a0.round

    ,a0.agent_0_episode_id
    ,a0.agent_0_action
    ,a0.agent_0_payoff
    ,a0.agent_0_ep_cumulative_score
    ,a0.agent_0_reasoning
    
    ,a1.agent_1_episode_id
    ,a1.agent_1_action
    ,a1.agent_1_payoff
    ,a1.agent_1_ep_cumulative_score
    ,a1.agent_1_reasoning
    
FROM 
    ipd2.results r
    
    -- Retrieve Agent 0 round details
    JOIN (
        SELECT 
            e.results_id
            ,e.episode_id           AS agent_0_episode_id
            ,e.episode
            ,rd.round
            ,rd.action              AS agent_0_action
            ,rd.payoff              AS agent_0_payoff
            ,rd.ep_cumulative_score AS agent_0_ep_cumulative_score
            ,rd.reasoning           AS agent_0_reasoning
        FROM ipd2.episodes e
            JOIN ipd2.rounds rd ON rd.episode_id = e.episode_id
        WHERE e.agent_idx = 0
    ) a0 ON a0.results_id = r.results_id

    -- Retrieve Agent 1 round details
    JOIN (
        SELECT 
            e.results_id
            ,e.episode_id           AS agent_1_episode_id
            ,e.episode
            ,rd.round
            ,rd.action              AS agent_1_action
            ,rd.payoff              AS agent_1_payoff
            ,rd.ep_cumulative_score AS agent_1_ep_cumulative_score
            ,rd.reasoning           AS agent_1_reasoning
        FROM ipd2.episodes e
            JOIN ipd2.rounds rd ON rd.episode_id = e.episode_id
        WHERE e.agent_idx = 1
    ) a1 ON a1.results_id = r.results_id
        and a1.episode = a0.episode
        and a1.round = a0.round
    
ORDER BY
    r.timestamp
    ,a0.episode
    ,a0.round
;

CREATE OR REPLACE VIEW ipd2.rounds_detail_vw AS
SELECT
    r.results_id
    ,r.filename
    ,r.username
    ,r.timestamp

    ,e.episode_id
    
    ,a.agent_idx
    ,e.episode
    ,rd.round

    ,CONCAT('agent_',  a.agent_idx) AS agent
    ,rd.action
    ,rd.payoff
    ,rd.ep_cumulative_score
    ,rd.reasoning

    ,e.score                        AS ep_score
    ,e.cooperations                 AS ep_cooperations
    ,e.cooperation_rate             AS ep_coop_rate
    ,e.reflection                   AS ep_reflection
    
FROM 
    ipd2.results r
    
    JOIN ipd2.llm_agents a
        ON a.results_id = r.results_id
        
    JOIN ipd2.episodes e
        ON e.results_id = r.results_id
        AND e.agent_idx = a.agent_idx

    JOIN ipd2.rounds rd
        ON rd.episode_id = e.episode_id
    
ORDER BY
    r.timestamp
    ,a.agent_idx
    ,e.episode
    ,rd.round
;

