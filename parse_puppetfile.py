import re

def parse_puppetfile(file_path):
    module_info = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r"^mod\s+'(?P<module>.*)',\s+:git\s+=>\s+'(?P<repo>.*)',\s+:branch\s+=>\s+'(?P<branch>.*)'", line)
            if match:
                module_name = match.group('module')
                git_link = match.group('repo')
                module_info.append((module_name, git_link))
    return module_info

if __name__ == "__main__":
    puppetfile_path = "Puppetfile"
    modules = parse_puppetfile(puppetfile_path)
    for module_name, git_link in modules:
        print(f"Module: {module_name}, Git Link: {git_link}")
