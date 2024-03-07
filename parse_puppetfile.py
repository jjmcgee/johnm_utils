import re

def parse_puppetfile(file_path):
    module_info = []
    with open(file_path, 'r') as file:
        for line in file:
            # Use regex to match lines containing module information
            match = re.match(r'^\s*mod\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]', line)
            if match:
                module_name = match.group(1)
                git_link = match.group(2)
                module_info.append((module_name, git_link))
    return module_info

if __name__ == "__main__":
    puppetfile_path = "Puppetfile"
    modules = parse_puppetfile(puppetfile_path)
    for module_name, git_link in modules:
        print(f"Module: {module_name}, Git Link: {git_link}")
