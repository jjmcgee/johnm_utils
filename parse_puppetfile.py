#!/usr/bin/env python
import subprocess
import os
import getpass
import optparse
import re

# Variable Declarations
git_bin = subprocess.run(['which', 'git'], capture_output=True, text=True).stdout.strip()
str_error_msg = "ERROR: Invalid input - "
environment_conf_contents = '''
modulepath = ./modules:$basemodulepath
'''
site_pp_contents = '''
File { backup => false }

node default {
  include jpmc_lib::ucm_puppet
}
'''
git_repo_lines = False

# Functions
def clear_all_vars():
  global git_bin, str_error_msg, site_pp_contents, environment_conf_contents
  git_bin = None
  str_error_msg = None
  site_pp_contents = None
  environment_conf_contents = None

def colorize(text, color_code):
  return f"\033[{color_code}m{text}\033[0m"

def red(text): 
  return colorize(text, 31)

def blue(text): 
  return colorize(text, 34)

# Option switches
parser = optparse.OptionParser()
parser.add_option("-f", "--puppetfile", dest="puppet_file", help="Puppet file to read")
parser.add_option("-d", "--environment", dest="puppet_env_dir", help="Environment directory to setup")
parser.add_option("-u", "--username", dest="git_username", help="GIT Bitbucket user name")
parser.add_option("-n", "--fullname", dest="user_fullname", help="Your full name")
parser.add_option("-e", "--email", dest="user_email", help="Your Email Address")
(options, args) = parser.parse_args()

print("===============================================================")
if not os.path.exists(git_bin):
  print(red('ERROR:GIT binary not found in the path:FAILED'))
  clear_all_vars()
  print("===============================================================")
  exit(1)

if options.puppet_file:
  puppetfile = options.puppet_file
  if os.path.exists(puppetfile):
    puppetfile_contents = open(puppetfile).read()
  else:
    print(f"{str_error_msg}puppetfile:FAILED")
    clear_all_vars()
    print("===============================================================")
    exit(1)
else:
  print(f"{str_error_msg}puppetfile: {red('FAILED')}")
  clear_all_vars()
  print("===============================================================")
  exit(1)

if options.puppet_env_dir:
  puppet_environment = options.puppet_env_dir.strip()
  if os.path.exists(puppet_environment):
    print(red('ERROR: Environment directory already exists. Please remove: '))
    print("===============================================================")
    clear_all_vars()
    exit(1)
  else:
    os.makedirs(puppet_environment)
    os.makedirs(os.path.join(puppet_environment, "modules"))
    os.makedirs(os.path.join(puppet_environment, "manifests"))
    os.makedirs(os.path.join(puppet_environment, "hieradata"))
else:
  print(f"{red(str_error_msg)}environment directory:FAILED")
  print("===============================================================")
  clear_all_vars()
  exit(1)

if options.git_username:
  git_username = options.git_username.strip()
else:
  print(f"{str_error_msg}GIT username:FAILED")
  print("===============================================================")
  clear_all_vars()
  exit(1)

if options.user_fullname:
  user_fullname = options.user_fullname.strip()
else:
  print(f"{str_error_msg}User Full Name:FAILED")
  print("===============================================================")
  clear_all_vars()
  exit(1)

if options.user_email:
  user_email = options.user_email.strip()
else:
  print(f"{str_error_msg}User Email Address:FAILED")
  print("===============================================================")
  clear_all_vars()
  exit(1)

git_password = getpass.getpass("Please enter your git bitbucket password: ")

git_askpass_file = f"/usr/local/bin/.git_askpass.{git_username}"
git_askpass_script = "#!/bin/ksh\necho $GIT_PASSWORD\n"
with open(git_askpass_file, 'w') as f:
  f.write(git_askpass_script)
os.chmod(git_askpass_file, 0o755)

os.environ['GIT_PASSWORD'] = git_password
os.environ['GIT_ASKPASS'] = git_askpass_file

# Processing starts here
with open(os.path.join(puppet_environment, "environment.conf"), 'w') as f:
  f.write(environment_conf_contents)

with open(os.path.join(puppet_environment, "manifests", "site.pp"), 'w') as f:
  f.write(site_pp_contents)

print("=======================================================================")
print(blue("INFO: All inputs are validated. Creating the environment. Please wait!!"))
print("=======================================================================")

for line in puppetfile_contents.splitlines():
  parts = None
  if parts := re.match(r'^mod\s+\'(?P<module>.*)\',\s+:git\s+=>\s+\'(?P<repo>https?://.*)\'', line):
    git_repo_lines = True
    puppet_module = parts['module']
    repo = parts['repo']

    command = f"{git_bin} clone {repo} {os.path.join(puppet_environment, 'modules', puppet_module)}"
    print(f"Running: {command}")
    subprocess.run(command.split()) 
    command = f"{git_bin} --git-dir={os.path.join(puppet_environment, 'modules', puppet_module, '.git')} config user.name '{user_fullname}'"
    print(f"Running: {command}")
    subprocess.run(command.split()) 
    command = f"{git_bin} --git-dir={os.path.join(puppet_environment, 'modules', puppet_module, '.git')} config user.email '{user_email}'"
    print(f"Running: {command}")
    subprocess.run(command.split()) 

if git_repo_lines == False:
  print(red("WARNING:No GIT repo modules found.Standard Environment is created!"))
clear_all_vars()
print("===============================================================================")
print(blue("INFO: Setup completed.Env created under #{$puppet_environment}"))
print("===============================================================================")
