import altair as alt
import pandas as pd
import argparse

def vega_to_svg(input_file, output_file):
    """
    將 Vega JSON 檔案轉換為 SVG 圖檔

    Args:
        input_file (str): 輸入的 Vega JSON 檔案路徑
        output_file (str): 輸出的 SVG 檔案路徑
    """

    # 讀取 Vega JSON 檔案
    with open(input_file, 'r') as f:
        vega_spec = alt.from_json(f)

    # 渲染圖表並保存為 SVG
    chart = alt.Chart(vega_spec).to_chart()
    chart.save(output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Vega JSON to SVG')
    parser.add_argument('-i', '--input', required=True, help='Input Vega JSON file')
    parser.add_argument('-o', '--output', required=True, help='Output SVG file')
    args = parser.parse_args()

    vega_to_svg(args.input, args.output)