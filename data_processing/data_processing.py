import pandas as pd
import logging
import numpy as np
logging.basicConfig(filename='data_processing.log', level=logging.INFO,
format='%(asctime)s:%(levelname)s:%(message)s')
def read_data(file_path: str) -> pd.DataFrame:
"""Reads data from a CSV file into a pandas DataFrame.
Args:
file_path (str): The location of the file to read.
Returns:
pd.DataFrame: A DataFrame containing the read data.
"""
try:
data = pd.read_csv(file_path)
logging.info(f'Successfully read data from {file_path}')
return data
except FileNotFoundError:
logging.error(f'File {file_path} not found')
raise
except Exception as e:
logging.error(f'Error occurred while reading file {file_path}: {e}')
raise
def analyze_data(data: pd.DataFrame) -> dict:
"""Performs basic statistical analysis on the data.
Args:
data (pd.DataFrame): The data to analyze.
Returns:
dict: A summary of the data's statistical properties.
"""
try:
summary = data.describe(include='all').to_dict()
logging.info('Successfully analyzed data')
return summary
except Exception as e:
logging.error(f'Error occurred while analyzing data: {e}')
raise
def generate_report(summary: dict, output_path: str = 'summary_report.txt') -> None:
"""Generates a summary report of the data analysis.
Args:
summary (dict): The summary to write to the report.
output_path (str, optional): The location to write the report to. Defaults to 'summary_report.txt'.
"""
try:
with open(output_path, 'w') as f:
for key, value in summary.items():
f.write(f'{key}: {value}\n')
logging.info(f'Successfully wrote report to {output_path}')
except Exception as e:
logging.error(f'Error occurred while writing report: {e}')
raise
def main(file_path: str, output_path: str = 'summary_report.txt') -> None:
data = read_data(file_path)
summary = analyze_data(data)
generate_report(summary, output_path)