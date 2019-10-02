import os

DWH = {
    'SCHEMA': 'data_science',
    'NAME': 'dwh_prod',  # Must coincide with name in secrets.csv
}

projects_dir = '/Users/chriscollins/Documents/GitHub/dash_example'
sql_dir = os.path.join(projects_dir, 'sql')
data_dir = os.path.join(projects_dir, 'data')
