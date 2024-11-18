import pandas as pd
import altair as alt
from datetime import datetime, timedelta

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

# 計算最終的 start_date 總數
final_start_count = len(df['start_date'])

# 初始化計數器
values = []
open_count = 0
close_count = 0

# 計算每天的累積值
for date in date_range:
    # 計算當天新增的open數量
    open_count += len(df[df['start_date'] == date])
    
    # 計算當天新增的close數量
    close_count += len(df[df['finish_date'] == date])
    
    current_date = date.strftime('%Y-%m-%d')
    
    # 檢查是否為milestone日期
    bar_value = final_start_count if current_date in milestone_dates else 0
    
    # 將結果加入列表
    values.append({
        'date': current_date,
        'open': int(open_count),
        'close': int(close_count),
        'bar': int(bar_value)
    })

# 將資料轉換為DataFrame
chart_df = pd.DataFrame(values)
chart_df['date'] = pd.to_datetime(chart_df['date'])

# 創建折線圖
line_chart = alt.Chart(chart_df).mark_line().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('open:Q', title='Count'),
    color=alt.value('#1f77b4')
).properties(
    width=800,
    height=400
)

line_chart2 = alt.Chart(chart_df).mark_line().encode(
    x=alt.X('date:T'),
    y=alt.Y('close:Q'),
    color=alt.value('#ff7f0e')
)

# 創建長條圖
bar_chart = alt.Chart(chart_df).mark_bar(width=2).encode(
    x=alt.X('date:T'),
    y=alt.Y('bar:Q'),
    color=alt.value('#2ca02c')
)

# 合併圖表
final_chart = (line_chart + line_chart2 + bar_chart).properties(
    title='Bug Tracking Cumulative Chart'
)

# 添加圖例
legend_data = pd.DataFrame([
    {'category': 'Open', 'color': '#1f77b4'},
    {'category': 'Close', 'color': '#ff7f0e'},
    {'category': 'Milestone', 'color': '#2ca02c'}
])

legend = alt.Chart(legend_data).mark_point().encode(
    y=alt.Y('category:N', axis=alt.Axis(orient='right')),
    color=alt.Color('color:N', scale=None)
).properties(
    width=100,
    height=100
)

# 儲存為SVG檔案
final_chart.save('output_chart.svg')
#final_chart.save('output_chart.pdf')

# 如果你也想要互動式的HTML版本
final_chart.save('output_chart.html')

print("Chart files have been generated successfully!")