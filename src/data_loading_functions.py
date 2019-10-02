import logging
import os
import time
import pandas as pd
import pymysql
import psycopg2
from copy import deepcopy

from configuration import projects_dir, sql_dir, data_dir, DWH

# Create a dictionary for all needed settings in the current environment
settings = dict()
settings['connections'] = dict()
# Connection credentials
df_con = pd.read_csv(os.path.join(projects_dir, 'secrets.csv'))
for dbname in [DWH['NAME'], 'dwh-churn', 'livedb']:
    db_row = df_con[df_con['name'] == dbname].copy()
    if db_row.empty:
        print("{} is not listed on the secrets file!".format(dbname))
        continue
    connection_name, host, port, db, user, password = db_row.values[0]
    settings['connections'][dbname] = dict()
    settings['connections'][dbname]['host'] = host
    settings['connections'][dbname]['port'] = port
    if 'dwh' in dbname:
        settings['connections'][dbname]['dbname'] = db
    elif 'livedb' in dbname:
        settings['connections'][dbname]['db'] = db
    settings['connections'][dbname]['user'] = user
    settings['connections'][dbname]['password'] = password


def time_function(func):
    """A decorator to tell you how long each function took to run"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logging.info('Function {} completed in {} seconds'.format(
            func.__name__, round(time.time() - start_time)))
        return result
    return wrapper

def get_connection(dbname):
    params = deepcopy(settings['connections'][dbname])
    try:
        if 'livedb' in dbname.lower():
            con = pymysql.connect(**params)
        elif 'dwh' in dbname.lower():
            con = psycopg2.connect(**params)
        else:
            print("Connection named {} is not defined!".format(dbname))
            con = None
    except ConnectionError as e:
        print("Couldn't connect to {}".format(dbname))
        print(e)
        con = None
    return con


def run_sql_file(sql_path, params=None):
    with open(sql_path, "r") as f:
        sql_query = f.read()
    if params:
        sql_query = sql_query.format(**params)
    # For some reason if we define conn in a 'with' statement
    # we get an error 'Cursor' object has no attribute 'cursor'
    db = DWH["NAME"]
    conn = get_connection(db)
    df = pd.read_sql(sql_query, con=conn)
    return df

@time_function
def get_normal_churn_rate(download=False, debug=False):
    logging.info('Running get_normal_churn_rate()')
    path = os.path.join(data_dir, 'churn_performance_10_normal_churn_data.csv')
    if os.path.isfile(path) and download is False:
        logging.info(
            'Loading existing file and appending new data if applicable')
        df = pd.read_csv(path, index_col=False)
        if debug is False:
            # Get a list of all periods existing in the data so far
            periods = df['period'].drop_duplicates()
            latest_period = max(periods)
            # Download all data after the latest period in the .csv
            params = {'latest_period': latest_period}
            df_new = run_sql_file(
                os.path.join(sql_dir, 'churn_performance_10_normal_churn.sql'),
                params)
            logging.info('Rows to be added: {}'.format(len(df_new)))
            df = df.append(df_new)
    else:
        logging.info('Running complete refresh of data')
        params = {'latest_period': 201920}
        df = run_sql_file(
            os.path.join(sql_dir, 'churn_performance_10_normal_churn.sql'),
        params)
    df.to_csv(path)
    # Sort by period and set this as the row index
    df = df.sort_values('period')
    df.index = df['period']
    return df


@time_function
def get_latest_churn_rate(download=False, debug=False):
    logging.info('Running get_latest_churn_rate()')
    path = os.path.join(data_dir, 'churn_performance_2_latest_churn_data.csv')
    if os.path.isfile(path) and download is False:
        logging.info(
            'Loading existing file and appending new data if applicable')
        df = pd.read_csv(path, index_col=False)
        if debug is False:
            # Get a list of all periods existing in the data so far
            periods = df['period'].drop_duplicates()
            latest_period = max(periods)
            # Download all data after the latest period in the .csv
            params = {'latest_period': latest_period}
            df_new = run_sql_file(
                os.path.join(sql_dir, 'churn_performance_2_latest_churn.sql'),
            params)
            logging.info('Rows to be added: {}'.format(len(df_new)))
            df = df.append(df_new)
    else:
        logging.info('Running complete refresh of data')
        params = {'latest_period': 201920}
        df = run_sql_file(
            os.path.join(sql_dir, 'churn_performance_2_latest_churn.sql'),
        params)
    df.to_csv(path)
    # Sort by period and set this as the row index
    df = df.sort_values('period')
    df.index = df['period']
    return df


@time_function
def get_churn_metrics(download=False, debug=False):
    logging.info('Running get_churn_metrics()')
    path = os.path.join(data_dir, 'churn_performance_1_metrics_data.csv')
    if os.path.isfile(path) and download is False:
        logging.info(
            'Loading existing file and appending new data if applicable')
        df = pd.read_csv(path, index_col=False)
        if debug is False:
            # Get a list of all periods existing in the data so far
            periods = df['period'].drop_duplicates()
            latest_period = max(periods)
            # Download all data after the latest period in the .csv
            params = {'latest_period': latest_period}
            df_new = run_sql_file(
                os.path.join(sql_dir, 'churn_performance_1_metrics.sql'),
            params)
            logging.info('Rows to be added: {}'.format(len(df_new)))
            df = df.append(df_new).drop_duplicates()
    else:
        logging.info('Running complete refresh of data')
        params = {'latest_period': 201920}
        df = run_sql_file(
            os.path.join(sql_dir, 'churn_performance_1_metrics.sql'),
        params)
    df.to_csv(path)
    # Sort by period and set this as the row index
    df = df.sort_values('period')
    df.index = df['period']
    return df
