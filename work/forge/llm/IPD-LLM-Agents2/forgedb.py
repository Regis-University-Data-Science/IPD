"""
    FORGE Database ETL
    ETL Pipeline for Iterated Prisoner's Dilemma with LLM Agents

    Practicum I - MSDS 692/S41: Data Science Practicum I

    Emily D. Carpenter
    Anderson College of Business and Computing, Regis University

    Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf

    February 2026
"""

import argparse
import glob
import json
import logging
import os

import pandas as pd
import psycopg
from psycopg.rows import dict_row

script_dir = os.path.dirname(os.path.abspath(__file__))

# Set up logging
logging.basicConfig(
    filename=os.path.join(script_dir, 'forgedb.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ForgeDB:
    def __init__(self, host='platinum', dbname='forge', user=None):
        """Initialize connection to the forge database."""
        if user is None:
            import getpass
            user = getpass.getuser()
        
        self.conn = psycopg.connect(
            host=host,
            dbname=dbname,
            user=user,
            row_factory=dict_row
        )
    
    def close(self):
        """Close the database connection."""
        self.conn.close()

    # ==========================================================================
    # Methods for querying the database
    # ==========================================================================
    def query(self, sql, params=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
        
    def get_results(self, start_date=None, end_date=None, username=None, filename=None, limit=None ):
        """
        Query Iterative Prisoner's Dilemma (IPD) game results and return as a pandas DataFrame.

        This query returns all data for a given experiment with each row representing
        a single round of IPD data per agent. 
        
        **Note:** Columns will contain duplicate data and require grouping for data analysis.
        
        Parameters:
            start_date: Filter results on or after this date (string or datetime)
            end_date:   Filter results on or before this date (string or datetime)
            username:   Filter by username (full or partial, % is wildcard char, case insensitive)
            filename:   Filter by name of the results JSON file (full or partial, 
                            % is wildcard, case insensitive)
            limit:      Maximum rows to return

        Example Usage:
            db.get_results(username='dhart')
            db.get_results(username='dhart', filename='%ep50%') # get all filenames with ep50
            db.get_results(
                username='dhart',
                filename='%ep50%',
                start_date='2026-01-25',
                end_date='2026-01-26 17:00:00')
        """
        return self._query_view('results_vw', start_date=start_date, end_date=end_date, 
            username=username, filename=filename, limit=limit)

    def get_summary(self, start_date=None, end_date=None, username=None, filename=None, limit=None ):
        """
        Query Iterative Prisoner's Dilemma (IPD) game results and return as a pandas DataFrame.

        This query returns summary data for a given experiment with each row containing distinct
        data. Agent data has been pivoted to columns for ease of data analysis.

        Parameters:
            start_date: Filter results on or after this date (string or datetime)
            end_date:   Filter results on or before this date (string or datetime)
            username:   Filter by username (full or partial, % is wildcard char, case insensitive)
            filename:   Filter by name of the results JSON file (full or partial, 
                            % is wildcard, case insensitive)
            limit:      Maximum rows to return

        Example Usage:
            db.get_results(username='dhart')
            db.get_results(username='dhart', filename='%ep50%') # get all filenames with ep50
            db.get_results(
                username='dhart',
                filename='%ep50%',
                start_date='2026-01-25',
                end_date='2026-01-26 17:00:00')
        """
        return self._query_view('session_summary_vw', start_date=start_date, end_date=end_date, 
            username=username, filename=filename, limit=limit)

    def get_rounds(self, start_date=None, end_date=None, username=None, filename=None, limit=None ):
        """
        Query Iterative Prisoner's Dilemma (IPD) game results and return as a pandas DataFrame.

        This query returns detailed data on each agent per rounds.
        **Note:** Columns will contain duplicate data and require grouping for data analysis.

        Parameters:
            start_date: Filter results on or after this date (string or datetime)
            end_date:   Filter results on or before this date (string or datetime)
            username:   Filter by username (full or partial, % is wildcard char, case insensitive)
            filename:   Filter by name of the results JSON file (full or partial, 
                            % is wildcard, case insensitive)
            limit:      Maximum rows to return

        Example Usage:
            db.get_results(username='dhart')
            db.get_results(username='dhart', filename='%ep50%') # get all filenames with ep50
            db.get_results(
                username='dhart',
                filename='%ep50%',
                start_date='2026-01-25',
                end_date='2026-01-26 17:00:00')
        """
        return self._query_view('rounds_detail_vw', start_date=start_date, end_date=end_date, 
            username=username, filename=filename, limit=limit)

    def _query_view(self, view_name, start_date=None, end_date=None, username=None, filename=None, limit=None):
        try:
            sql = f"SELECT * FROM ipd2.{view_name} WHERE 1=1"
            params = {}
            
            if start_date is not None:
                sql += " AND timestamp >= %(start_date)s"
                params['start_date'] = start_date
            
            if end_date is not None:
                sql += " AND timestamp < %(end_date)s"
                params['end_date'] = end_date
            
            if username is not None:
                sql += " AND LOWER(username) LIKE LOWER(%(username)s)"
                params['username'] = username

            if filename is not None:
                sql += " AND LOWER(filename) LIKE LOWER(%(filename)s)"
                params['filename'] = filename
                        
            if limit is not None:
                sql += f" LIMIT {limit}"
            
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            
            df = pd.DataFrame(rows)
            return df
        
        except Exception as e:
            logging.error(f"get_results failed - {e}")
            raise

    # ==========================================================================
    # Methods for importing results JSON files into the database
    # ==========================================================================
    def load_json(self, filepath, user_name='unknown'):
        """
        Import a JSON file into the database.
        
        The INSERT uses parameterized queries where %(name)s placeholders
        are replaced with values from a dictionary. This prevents SQL
        injection and handles type conversion automatically.
        """

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

                # Capture the results filename
                filename = os.path.basename(filepath)

                # Set username for older JSON file versions
                researcher = data.get('username', user_name)
            
            # Insert into results table, retrieve serialized results_id from insert
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ipd2.results (
                        filename
                        ,timestamp
                        ,hostname
                        ,username
                        ,elapsed_seconds
                        ,cfg_num_episodes
                        ,cfg_round_per_episode
                        ,cfg_total_rounds
                        ,cfg_history_window_size
                        ,cfg_temperature
                        ,cfg_reset_between_episodes
                        ,cfg_reflection_type
                        ,cfg_decision_token_limit
                        ,cfg_reflection_token_limit
                        ,cfg_http_timeout
                        ,cfg_force_decision_retries
                        ,system_prompt
                        ,reflection_template
                        ,raw_json
                    ) VALUES (
                        %(filename)s
                        ,%(timestamp)s
                        ,%(hostname)s
                        ,%(username)s
                        ,%(elapsed_seconds)s
                        ,%(num_episodes)s
                        ,%(rounds_per_episode)s
                        ,%(total_rounds)s
                        ,%(history_window_size)s
                        ,%(temperature)s
                        ,%(reset_between_episodes)s
                        ,%(reflection_type)s
                        ,%(decision_token_limit)s
                        ,%(reflection_token_limit)s
                        ,%(http_timeout)s
                        ,%(force_decision_retries)s
                        ,%(system_prompt)s
                        ,%(reflection_template)s
                        ,%(raw_json)s
                    ) RETURNING results_id
                    """, 
                    {
                        # Session metadata
                        'filename':                 filename,
                        'timestamp':                data['timestamp'],
                        'hostname':                 data.get('hostname', None),
                        'username':                 researcher,
                        'elapsed_seconds':          data['elapsed_seconds'],
                        
                        # Config fields
                        'num_episodes':             data['config']['num_episodes'],
                        'rounds_per_episode':       data['config']['rounds_per_episode'],
                        'total_rounds':             data['config']['total_rounds'],
                        'history_window_size':      data['config']['history_window_size'],
                        'temperature':              data['config']['temperature'],
                        'reset_between_episodes':   data['config']['reset_between_episodes'],
                        'reflection_type':          data['config']['reflection_type'],
                        'decision_token_limit':     data['config']['decision_token_limit'],
                        'reflection_token_limit':   data['config']['reflection_token_limit'],
                        'http_timeout':             data['config']['http_timeout'],
                        'force_decision_retries':   data['config']['force_decision_retries'],
                        
                        # Prompts
                        'system_prompt':            data['prompts']['system_prompt'],
                        'reflection_template':      data['prompts']['reflection_template'],
                        
                        # Raw JSON
                        'raw_json':                 json.dumps(data)
                    })
                
                # Retrieve the serialized key generated for the results table
                results_id = cur.fetchone()['results_id']
            
                # Insert into llm_agents table (variable number of agents)
                agent_idx = 0
                while f'agent_{agent_idx}' in data:
                    agent_key = f'agent_{agent_idx}'
                    host_key = f'host_{agent_idx}'
                    model_key = f'model_{agent_idx}'
                    
                    cur.execute("""
                        INSERT INTO ipd2.llm_agents (
                            results_id
                            ,agent_idx
                            ,host
                            ,agent_model
                            ,cfg_model
                            ,total_score
                            ,total_cooperations
                            ,overall_cooperation_rate
                        ) VALUES (
                            %(results_id)s
                            ,%(agent_idx)s
                            ,%(host)s
                            ,%(agent_model)s
                            ,%(cfg_model)s
                            ,%(total_score)s
                            ,%(total_cooperations)s
                            ,%(overall_cooperation_rate)s
                        )
                    """,
                    {
                        'results_id':              results_id,
                        'agent_idx':               agent_idx,
                        'host':                    data.get(host_key, None),
                        'agent_model':             data[agent_key]['model'],
                        'cfg_model':               data['config'][model_key],
                        'total_score':             data[agent_key]['total_score'],
                        'total_cooperations':      data[agent_key]['total_cooperations'],
                        'overall_cooperation_rate': data[agent_key]['overall_cooperation_rate']
                    })
                    
                    agent_idx += 1

                # Insert into episodes table
                for episode_data in data['episodes']:
                    episode_num = episode_data['episode']
                    
                    # Loop through agents for this episode
                    agent_idx = 0
                    while f'agent_{agent_idx}' in episode_data:
                        agent_key = f'agent_{agent_idx}'
                        
                        cur.execute("""
                            INSERT INTO ipd2.episodes (
                                results_id
                                ,agent_idx
                                ,episode
                                ,score
                                ,cooperations
                                ,cooperation_rate
                                ,reflection
                            ) VALUES (
                                %(results_id)s
                                ,%(agent_idx)s
                                ,%(episode)s
                                ,%(score)s
                                ,%(cooperations)s
                                ,%(cooperation_rate)s
                                ,%(reflection)s
                            ) RETURNING episode_id
                        """,
                        {
                            'results_id':       results_id,
                            'agent_idx':        agent_idx,
                            'episode':          episode_num,
                            'score':            episode_data[agent_key]['episode_score'],
                            'cooperations':     episode_data[agent_key]['cooperations'],
                            'cooperation_rate': episode_data[agent_key]['cooperation_rate'],
                            'reflection':       episode_data[agent_key]['reflection']
                        })
                        
                        episode_id = cur.fetchone()['episode_id']
                        
                        # Insert rounds for this episode/agent
                        for round_data in episode_data['rounds']:
                            action_key = f'agent_{agent_idx}_action'
                            reasoning_key = f'agent_{agent_idx}_reasoning'
                            payoff_key = f'agent_{agent_idx}_payoff'
                            ep_score_key = f'agent_{agent_idx}_episode_score'
                            
                            cur.execute("""
                                INSERT INTO ipd2.rounds (
                                    episode_id
                                    ,round
                                    ,action
                                    ,payoff
                                    ,ep_cumulative_score
                                    ,reasoning
                                ) VALUES (
                                    %(episode_id)s
                                    ,%(round)s
                                    ,%(action)s
                                    ,%(payoff)s
                                    ,%(ep_cumulative_score)s
                                    ,%(reasoning)s
                                )
                            """,
                            {
                                'episode_id':          episode_id,
                                'round':               round_data['round'],
                                'action':              round_data[action_key],
                                'payoff':              round_data[payoff_key],
                                'ep_cumulative_score': round_data[ep_score_key],
                                'reasoning':           round_data[reasoning_key]
                            })
                        
                        agent_idx += 1

            self.conn.commit()
            logging.info(
                f"Loaded {filepath} -> results_id={results_id}, user={researcher}")
            return (results_id, researcher)
        
        # Prevent duplicate test results from import
        except psycopg.errors.UniqueViolation as e:
            self.conn.rollback()
            logging.warning(f"Duplicate file skipped: {filepath} - {e}")
            return None
        
        # Unexpected exception occurred
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Failed to load {filepath} - {e}")
            raise


    def _load_batch(self, source, pattern='*.json', user_name='unknown'):
        """ Load JSON files from a directory or a list of filepaths.
            To be used in CLI environment only.
        """
        
        if isinstance(source, list):
            filepaths = source
        else:
            filepaths = glob.glob(os.path.join(source, pattern))
        
        if not filepaths:
            logging.warning(f"No files to process")
            return {'loaded': [], 'skipped': [], 'failed': []}
        
        logging.info(f"Processing {len(filepaths)} files")
        
        results = {
            'loaded': [],
            'skipped': [],
            'failed': []
        }
        
        for filepath in sorted(filepaths):
            try:
                result = self.load_json(filepath, user_name)
                
                if result is not None:
                    results['loaded'].append((filepath, result[0], result[1]))
                else:
                    results['skipped'].append(filepath)
                    
            except Exception as e:
                results['failed'].append((filepath, str(e)))
        
        logging.info(f"Batch complete: {len(results['loaded'])} loaded, "
                    f"{len(results['skipped'])} skipped, "
                    f"{len(results['failed'])} failed")
        
        return results
    
    def get_files(self, path, user_name='unknown'):
        """ Load a file, directory, or glob pattern.
            To be used in CLI environment only.
        """
        
        if os.path.isfile(path):
            return self.load_json(path, user_name)
        
        elif os.path.isdir(path):
            return self._load_batch(path, user_name=user_name)
        
        elif '*' in path or '?' in path:
            dirpath = os.path.dirname(path) or '.'
            pattern = os.path.basename(path)
            return self._load_batch(dirpath, pattern, user_name)
        
        else:
            logging.error(f"Path not found: {path}")
            return None

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load IPD game data into PostgreSQL')
    parser.add_argument('--import', dest='import_path', nargs='*', help='File(s), directory, or pattern to load')
    parser.add_argument('--username', dest='user_name', default='unknown', help='Default username for older files missing username field')
    
    args = parser.parse_args()
    
    if args.import_path:
        db = ForgeDB()
        
        if len(args.import_path) == 1:
            result = db.get_files(args.import_path[0], args.user_name)
            
            if isinstance(result, tuple):
                print(f"Loaded: results_id {result[0]}, user {result[1]}")
            elif isinstance(result, dict):
                print(f"Loaded: {len(result['loaded'])}, Skipped: {len(result['skipped'])}, Failed: {len(result['failed'])}")
        else:
            results = db._load_batch(args.import_path, user_name=args.user_name)
            print(f"Loaded: {len(results['loaded'])}, Skipped: {len(results['skipped'])}, Failed: {len(results['failed'])}")
        
        db.close()
    else:
        parser.print_help()