import pandas as pd
from datetime import datetime, timedelta
import json

# 讀取CSV檔案
df = pd.read_csv('data.csv')

# 將日期欄位轉換為datetime格式
df['start_date'] = pd.to_datetime(df['start_date'])
df['finish_date'] = pd.to_datetime(df['finish_date'])

# 找出整個日期範圍
start_date = df['start_date'].min()
end_date = df['finish_date'].max()

# 創建日期範圍
date_range = pd.date_range(start=start_date, end=end_date)

# 初始化計數器
cumulative_data = []
open_count = 0
close_count = 0

# 計算每天的累積值
for date in date_range:
    # 計算當天新增的open數量
    open_count += len(df[df['start_date'] == date])
    
    # 計算當天新增的close數量
    close_count += len(df[df['finish_date'] == date])
    
    # 將結果加入列表
    cumulative_data.append({
        'date': date.strftime('%Y-%m-%d'),
        'open': int(open_count),
        'close': int(close_count)
    })

# 將結果轉換為想要的格式並寫入檔案
with open('cumulative_curve.json', 'w') as f:
    for item in cumulative_data:
        json.dump(item, f, separators=(',', ':'))
        f.write('\n')

# 印出結果
for item in cumulative_data:
    print(json.dumps(item, separators=(',', ':')))