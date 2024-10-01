import os
import pandas as pd
from collections import Counter

def get_all_attributes(directory):
    all_attributes = set()
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = pd.read_excel(file_path, usecols='H')
            all_attributes.update(df.iloc[:, 0].unique())
    return sorted(all_attributes)

def count_attributes(directory, all_attributes):
    results = []
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = pd.read_excel(file_path, usecols='H')
            attribute_counts = Counter(df.iloc[:, 0])
            
            row = [filename] + [attribute_counts.get(attr, 0) for attr in all_attributes]
            results.append(row)
    return results

def main():
    directory = 'reg_gen'
    all_attributes = get_all_attributes(directory)
    results = count_attributes(directory, all_attributes)
    
    header = ['Filename'] + all_attributes
    df_results = pd.DataFrame(results, columns=header)
    df_results.to_csv('attr.csv', index=False)
    print("結果已保存到 attr.csv")

if __name__ == "__main__":
    main()