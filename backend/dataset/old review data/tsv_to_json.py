import pandas as pd

input_path = 'title.basics.tsv/title.basics.tsv'
output_path = 'data.jsonl'

with open(output_path, 'w', encoding='utf-8') as f:
    for chunk in pd.read_csv(input_path, sep='\t', chunksize=100000):
        chunk.to_json(f, orient='records', lines=True)