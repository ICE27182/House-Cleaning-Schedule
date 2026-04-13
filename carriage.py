
from os import walk

def modify_carriage(path: str):
    with open(path, 'r') as f:
        content = f.read()
    content = content.replace('\r\n', '\n')
    with open(path, 'w') as f:
        f.write(content)

target_suffixes = ['.py', '.txt', '.md', ".jsx", ".js", ".html", ".css", ".json", ".yml", ".yaml", ".gitignore"]
for (dirpath, dirnames, filenames) in walk('backend'):
    for filename in filenames:
        if any(filename.endswith(suffix) for suffix in target_suffixes):
            modify_carriage(f'{dirpath}/{filename}')
