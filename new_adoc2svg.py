import os
import re
import requests
import base64
import zlib

def extract_kroki_block(file_path):
    """
    Extract Kroki diagram block from an AsciiDoc file.
    
    :param file_path: Path to the .adoc file
    :return: Tuple of (diagram_type, diagram_content) or None if no Kroki diagram found
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regex to match various Kroki diagram blocks
    kroki_patterns = [
        # Handle [kroki, type=...] blocks
        r'\[kroki.*type=(["\']?)(\w+)\1\]\n----\n(.*?)\n----',
        
        # Handle direct [plantuml] or other diagram type blocks
        r'\[(\w+)\]\n----\n(.*?)\n----',
        
        # Handle alternative block syntax with ...
        r'\[kroki,.*type=(["\']?)(\w+)\1\]\n\.\.\.\n(.*?)\n\.\.\.',
        
        # Handle direct type blocks with ...
        r'\[(\w+)\]\n\.\.\.\n(.*?)\n\.\.\.',
    ]
    
    for pattern in kroki_patterns:
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            # Determine diagram type and content based on match groups
            if len(match.groups()) == 3:  # For patterns with 3 groups
                return match.group(2), match.group(3).strip()
            elif len(match.groups()) == 2:  # For patterns with 2 groups
                return match.group(1), match.group(2).strip()
    
    return None

def convert_to_kroki_url(diagram_type, diagram_content):
    """
    Convert diagram content to Kroki diagram URL.
    
    :param diagram_type: Type of diagram (plantuml, mermaid, etc.)
    :param diagram_content: Diagram content
    :return: Kroki diagram URL
    """
    compressed = zlib.compress(diagram_content.encode('utf-8'))
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8').rstrip('=')
    return f'https://kroki.io/{diagram_type}/svg/{encoded}'

def download_image(url, output_path):
    """
    Download image from URL and save to specified path.
    
    :param url: Image URL
    :param output_path: Path to save the image
    """
    response = requests.get(url)
    response.raise_for_status()
    
    with open(output_path, 'wb') as file:
        file.write(response.content)

def process_directory(directory):
    """
    Process all .adoc files in the given directory, converting Kroki diagrams to SVG and PNG.
    
    :param directory: Directory path to process
    """
    for filename in os.listdir(directory):
        if filename.endswith('.adoc'):
            file_path = os.path.join(directory, filename)
            
            # Extract Kroki diagram
            kroki_info = extract_kroki_block(file_path)
            if not kroki_info:
                print(f"No Kroki diagram found in {filename}")
                continue
            
            diagram_type, diagram_content = kroki_info
            
            # Generate Kroki URL
            kroki_url = convert_to_kroki_url(diagram_type, diagram_content)
            
            # Base filename for output files
            base_filename = os.path.splitext(filename)[0]
            
            # Convert to SVG
            svg_path = os.path.join(directory, f'{base_filename}.svg')
            try:
                download_image(kroki_url, svg_path)
                print(f"SVG created: {svg_path}")
            except Exception as e:
                print(f"Error creating SVG for {filename}: {e}")
            
            # Convert to PNG (change URL to PNG)
            png_url = kroki_url.replace('/svg/', '/png/')
            png_path = os.path.join(directory, f'{base_filename}.png')
            try:
                download_image(png_url, png_path)
                print(f"PNG created: {png_path}")
            except Exception as e:
                print(f"Error creating PNG for {filename}: {e}")

def main():
    # Prompt user for directory path
    directory = input("Enter the directory path containing .adoc files: ").strip()
    
    # Validate directory
    if not os.path.isdir(directory):
        print("Invalid directory path.")
        return
    
    # Process the directory
    process_directory(directory)

if __name__ == '__main__':
    main()