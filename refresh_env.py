#!/bin/env python
#
# Description: This script should run as root, to refresh the puppet environment passed.
#   You are required to pass a file name that contains all the modules you want to pull.
#   To make this as easy as possible, make sure you have your ssh key added to bitbucket
#   Before running this script run as root: eval $(ssh-agent); ssh-add ~<sid>/.ssh/id_rsa
#   This allows root to use your ssh-key to pull from bitbucket.
#
import sys
import os
import getopt
import shutil
import re

environment_base = "/home/i024617/linux_home/scratch/code/environments"
# environment_base = "/etc/puppetlabs/code/environments"

def usage():
  print("This script will refresh the modules of the puppet environment passed along with the module list.")
  print("You need to have your public ssh key added to bitbucket for this to work.")
  print("BEFORE RUN: eval $(ssh-agent); ssh-add ~<sid>/.ssh/id_rsa ")
  print("Usage: {0} -h --help -e --environment -m --module-file <- all required to be passed.".format(sys.argv[0]))
  print("-h, --help           Script Usage.")
  print("-e, --environment    The puppet environment to refresh.")
  print("-m, --module-file    Path to the file containing the module list.")
  sys.exit()

# TODO keeping for reference will remove once all working.
def check_ssh_key(user):
 home_dir = "/home/{0}/linux_home".format(user)

 if not os.path.isfile("{0}/.ssh/id_rsa".format(home_dir, user)):
   print("You need your ssh-key aded to bitbucket. No ssh-key detected.")


def cleanup_env(environment):
  if os.path.exists("{0}/{1}".format(environment_base, environment)):
    print("INFO: Removing all modules in {0}/{1} environment.".format(environment_base, environment))
    shutil.rmtree("{0}/{1}/modules".format(environment_base, environment))
    os.makedirs("{0}/{1}/modules".format(environment_base, environment))
  else:
    print("ERROR: {0}/{1} does not exist.".format(environment_base, environment))

def parse_puppetfile(module_file):
  module_info = []
  with open(module_file, 'r') as file:
    for line in file:
      match = re.match(r'^mod\s+\'(?P<module>.*)\',\s+:git\s+=>\s+\'(?P<repo>https?://.*|ssh://.*)\'', line)
      if match:
        module_name = match.group('module')
        git_link = match.group('repo').split("'")[0]
        module_info.append((module_name, git_link))
  return module_info

def refresh_env(environment, module_file):
  if not os.path.isfile(module_file):
    print("ERROR: {} path provided does not exist. Pass the absolute file path.".format(module_file))
  else:
    print("INFO: Parsing module list...")
    modules = parse_puppetfile(module_file)

    # for module in modules.read().splitlines():
    for module_name, git_link in modules:
      print("INFO: Pulling {0} from bitbucket into {1}/{2}/modules/{3}".format(git_link, environment_base, environment, module_name))
      os.system("/bin/git clone {0} {1}/{2}/modules/{3}"
                .format(git_link, environment_base, environment, module_name))

    set_permissions(environment_base + "/" + environment + "/modules")

def set_permissions(module_path):
  print("INFO: Ensuring correct permissions pe-puppet:pe-puppet in modules dir: {}.".format(module_path))
  os.system("chown -R pe-puppet:pe-puppet {}".format(module_path))
  os.system("chmod -R 755 {}".format(module_path))

if __name__ == "__main__":
  opts = None
  args = None
  puppet_env = None
  module_list = None

  try:
    opts, args = getopt.getopt(
      sys.argv[1:], 'h:e:m:',
      ['help', 'environment=', 'module-file=']
    )
  except getopt.GetoptError as err_output:
    print("ERROR: ", err_output)
    usage()

  if opts:
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        usage()
      elif opt in ("-e", "--environment"):
        puppet_env = arg
        cleanup_env(puppet_env)
      elif opt in ("-m", "--module-file"):
        module_list = arg
        refresh_env(puppet_env, module_list)
  else: 
    usage()
