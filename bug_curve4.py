import pandas as pd
from datetime import datetime, timedelta
import json

# 讀取主要CSV檔案
df = pd.read_csv('data.csv')

# 讀取milestone CSV檔案
milestone_df = pd.read_csv('milestone.csv')
print("目前可用的欄位：", milestone_df.columns)
milestone_dates = set(pd.to_datetime(milestone_df['milestone_date']).dt.strftime('%Y-%m-%d'))

# 將日期欄位轉換為datetime格式
df['start_date'] = pd.to_datetime(df['start_date'])
df['finish_date'] = pd.to_datetime(df['finish_date'])

# 找出整個日期範圍
start_date = df['start_date'].min()
end_date = df['finish_date'].max()

# 創建日期範圍
date_range = pd.date_range(start=start_date, end=end_date)

# 初始化計數器
values = []
open_count = 0
close_count = 0

# 計算每天的累積值並記錄最大值
for date in date_range:
    # 計算當天新增的open數量
    open_count += len(df[df['start_date'] == date])
    
    # 計算當天新增的close數量
    close_count += len(df[df['finish_date'] == date])
    
    current_date = date.strftime('%Y-%m-%d')
    
    # 檢查是否為milestone日期
    # 如果是milestone日期，bar值設為open和close中的最大值
    # 如果不是milestone日期，bar值設為0
    bar_value = max(open_count, close_count) if current_date in milestone_dates else 0
    
    # 將結果加入列表
    values.append({
        'date': current_date,
        'open': int(open_count),
        'close': int(close_count),
        'bar': int(bar_value)
    })

# 創建最終的數據結構
output_data = {
    'data': {
        'values': values
    }
}

# 將結果轉換為JSON格式並寫入檔案
with open('cumulative_curve.json', 'w') as f:
    f.write('{\n  "data": {\n    "values": [\n')
    for i, value in enumerate(values):
        line = json.dumps(value, separators=(',', ':'))
        if i < len(values) - 1:
            f.write(f'      {line},\n')
        else:
            f.write(f'      {line}\n')
    f.write('    ]\n  }\n}')

# 印出結果
print('{\n  "data": {\n    "values": [')
for i, value in enumerate(values):
    line = json.dumps(value, separators=(',', ':'))
    if i < len(values) - 1:
        print(f'      {line},')
    else:
        print(f'      {line}')
print('    ]\n  }\n}')