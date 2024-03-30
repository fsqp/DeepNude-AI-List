import re
import time
import requests
from pathlib import Path

def extract_urls_from_readme(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    return [line for line in content if re.search(r'\*\s+\[.+\]\(http.+?\)', line)]

def fetch_html_content(url):
    start_time = time.time()
    try:
        response = requests.get(url)
        elapsed_time = time.time() - start_time
        if response.status_code == 200:
            return response.text, elapsed_time
        else:
            return None, "failed"
    except Exception as e:
        return None, "failed"

def write_html_to_file(folder_path, filename, content):
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    file_path = Path(folder_path) / f'{filename}.html'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    return file_path

def update_readme(readme_path, lines_with_times):
    with open(readme_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    
    updated_content = []
    for line in content:
        updated_line = line
        for desc, time_info in lines_with_times:
            if desc in line:
                if isinstance(time_info, float):
                    time_text = f'Speed {time_info:.2f} s.'
                else:
                    time_text = 'Access failed.'
                # Remove the old time
                updated_line = re.sub(r'Speed [0-9.]+ s\.|Access failed\.', '', line)

                # Add the new time
                updated_line = updated_line.rstrip() + ' ' + time_text + '\n'
                #updated_line = re.sub(r'(Speed [0-9.]+ s\.|Access failed\.)?\s*$', ' ' + time_text + '\n', line)
                break
        updated_content.append(updated_line)
    
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_content)

def main(readme_path='README.md', html_folder='html'):
    lines = extract_urls_from_readme(readme_path)
    lines_with_times = []
    
    for line in lines:
        match = re.search(r'\*\s+\[(.+)\]\((http.+?)\)', line)
        if match:
            desc, url = match.groups()
            print(f'Downloading {url}...')
            html_content, download_time = fetch_html_content(url)
            if html_content is not None:
                write_html_to_file(html_folder, desc.replace(' ', '_'), html_content)
            lines_with_times.append((desc, download_time))
    
    update_readme(readme_path, lines_with_times)

if __name__ == '__main__':
    main()
