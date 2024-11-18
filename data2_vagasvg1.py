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

# 建立 Vega 規格
vega_spec = {
    "$schema": "https://vega.github.io/schema/vega/v5.json",
    "width": 800,
    "height": 400,
    "padding": 5,
    "background": "white",
    
    "data": [
        {
            "name": "table",
            "values": values
        }
    ],
    
    "scales": [
        {
            "name": "x",
            "type": "time",
            "domain": {"data": "table", "field": "date"},
            "range": "width"
        },
        {
            "name": "y",
            "type": "linear",
            "domain": {
                "data": "table",
                "fields": ["open", "close", "bar"]
            },
            "nice": true,
            "range": "height"
        },
        {
            "name": "color",
            "type": "ordinal",
            "domain": ["Open", "Close", "Milestone"],
            "range": ["#1f77b4", "#ff7f0e", "#2ca02c"]
        }
    ],
    
    "axes": [
        {
            "scale": "x",
            "orient": "bottom",
            "title": "Date",
            "format": "%Y-%m-%d",
            "labelAngle": -45
        },
        {
            "scale": "y",
            "orient": "left",
            "title": "Count"
        }
    ],
    
    "marks": [
        {
            "type": "line",
            "from": {"data": "table"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "date"},
                    "y": {"scale": "y", "field": "open"},
                    "stroke": {"value": "#1f77b4"},
                    "strokeWidth": {"value": 2}
                }
            }
        },
        {
            "type": "line",
            "from": {"data": "table"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "date"},
                    "y": {"scale": "y", "field": "close"},
                    "stroke": {"value": "#ff7f0e"},
                    "strokeWidth": {"value": 2}
                }
            }
        },
        {
            "type": "rect",
            "from": {"data": "table"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "date"},
                    "width": {"value": 2},
                    "y": {"scale": "y", "field": "bar"},
                    "y2": {"scale": "y", "value": 0},
                    "fill": {"value": "#2ca02c"}
                }
            }
        }
    ],
    
    "legends": [
        {
            "fill": "color",
            "title": "Series",
            "encode": {
                "symbols": {
                    "enter": {
                        "fillOpacity": {"value": 1}
                    }
                }
            }
        }
    ]
}

# 將 Vega 規格寫入文件
with open('vega_spec.json', 'w', encoding='utf-8') as f:
    json.dump(vega_spec, f, ensure_ascii=False, indent=2)

# 使用 vega-cli 將規格轉換為 SVG
# 注意：需要先安裝 vega-cli (npm install -g vega-cli)
import subprocess

try:
    subprocess.run(['vg2svg', 'vega_spec.json', 'output_chart.svg'])
    print("SVG file has been generated successfully!")
except Exception as e:
    print(f"Error generating SVG: {e}")
    print("Please make sure vega-cli is installed (npm install -g vega-cli)")