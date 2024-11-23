#!/usr/bin/env python3
import sys
import re
import argparse

class FormatConverter:
    def __init__(self):
        self.adoc_block_pattern = r'\[(.*?)\]\n-{4,}\n(.*?)\n-{4,}'
        self.md_block_pattern = r'```(.*?)\n(.*?)\n```'

    def adoc_to_md(self, content):
        def replace_block(match):
            format_type = match.group(1)
            block_content = match.group(2)
            return f"```{format_type}\n{block_content}\n```"
        
        return re.sub(self.adoc_block_pattern, replace_block, content, flags=re.DOTALL)

    def md_to_adoc(self, content):
        def replace_block(match):
            format_type = match.group(1)
            block_content = match.group(2)
            return f"[{format_type}]\n----\n{block_content}\n----"
        
        return re.sub(self.md_block_pattern, replace_block, content, flags=re.DOTALL)

def main():
    parser = argparse.ArgumentParser(description='Convert between AsciiDoc and Markdown formats')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('--to-md', action='store_true', help='Convert from AsciiDoc to Markdown')
    parser.add_argument('--to-adoc', action='store_true', help='Convert from Markdown to AsciiDoc')
    
    args = parser.parse_args()
    
    if args.to_md == args.to_adoc:
        print("Error: Please specify either --to-md or --to-adoc")
        sys.exit(1)
    
    converter = FormatConverter()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if args.to_md:
            converted_content = converter.adoc_to_md(content)
        else:
            converted_content = converter.md_to_adoc(content)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        
        print(f"Successfully converted {args.input} to {args.output}")
        
    except FileNotFoundError:
        print(f"Error: Could not find file {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
