#!/opt/puppetlabs/puppet/bin/ruby
require 'io/console'
require 'optparse'

###Variable Declarations###
$git_bin = (`which git`).chomp
$str_error_msg = "ERROR: Invalid input - "
$environment_conf_contents = '
modulepath = ./modules:$basemodulepath
'
$site_pp_contents = '
File { backup => false }

node default {
  include jpmc_lib::ucm_puppet
}
'
git_repo_lines = false

###Functions###
def clear_all_vars
  $git_bin = nil
  $str_error_msg = nil
  $site_pp_contents = nil
  $environment_conf_contents = nil
  git_askpass_file = nil
end

def colorize(text, color_code)
  "\e[#{color_code}m#{text}\e[0m"
end

def red(text); colorize(text, 31); end
def green(text); colorize(text, 32); end
def blue(text); colorize(text, 34); end


###Option switches###
begin
  options = {}
    OptionParser.new do |opts|
    opts.banner = "================================================================"
    opts.separator "Usage: setup_env -f | --puppetfile <puppet file name and path>
                 -d | --environment <Puppet environment directory>
                 -u | --username <git bitbucket username>
                 -n | --fullname <user full name>
                 -e | --email <user email address>"
    opts.separator "==============================================================="

    opts.on("-f", "--puppetfile PUPPETFILE", "Puppet file to read") do |f|
      options[:puppet_file] = f
    end
    opts.on("-d", "--environment ENV", "Environment directory to setup") do |d|
      options[:puppet_env_dir] = d
    end
    opts.on("-u", "--username USER", "GIT Bitbucket user name") do |u|
      options[:git_username] = u
    end
    opts.on("-n", "--fullname FULLNAME", "Your full name") do |n|
      options[:user_fullname] = n
    end
    opts.on("-e", "--email EMAIL", "Your Email Address") do |e|
      options[:user_email] = e
    end
    opts.on("-?", "--help", "Show usage") do
      puts opts
      exit 0
    end
end.parse!
end

puts "==============================================================="
if not File.exists?($git_bin)
  puts red('ERROR:GIT binary not found in the path:FAILED')
  clear_all_vars
  puts "==============================================================="
  exit 1
end
if options[:puppet_file]
  $puppetfile = options[:puppet_file]
  if File.exists?($puppetfile)
    $puppetfile_contents = File.read($puppetfile)
  else
    puts red("#{$str_error_msg}puppetfile:FAILED")
    clear_all_vars
    puts "==============================================================="
    exit 1
  end
else
  puts "#{$str_error_msg}puppetfile: " + red('FAILED')
  clear_all_vars
  puts "==============================================================="
  exit 1
end

if options[:puppet_env_dir]
  $puppet_environment = options[:puppet_env_dir].chomp
  if File.exists?($puppet_environment)
    puts red('ERROR: Environment directory already exists. Please remove: ')
    puts "==============================================================="
    clear_all_vars
    exit 1
  else
    Dir.mkdir($puppet_environment)
    Dir.mkdir($puppet_environment + "/modules")
    Dir.mkdir($puppet_environment + "/manifests")
    Dir.mkdir($puppet_environment + "/hieradata")
  end
else
  puts red("#{$str_error_msg}environment directory:FAILED")
  puts "==============================================================="
  clear_all_vars
  exit 1
end

if options[:git_username]
  $git_username = options[:git_username].chomp
else
  puts red("#{$str_error_msg}GIT username:FAILED")
  puts "==============================================================="
  clear_all_vars
  exit 1
end

if options[:user_fullname]
  $user_fullname = options[:user_fullname]
else
  puts red("#{$str_error_msg}User Full Name:FAILED")
  puts "==============================================================="
  clear_all_vars
  exit 1
end

if options[:user_email]
  $user_email = options[:user_email].chomp
else
  puts red("#{$str_error_msg}User Email Address:FAILED")
  puts "==============================================================="
  clear_all_vars
  exit 1
end

print "Please enter your git bitbucket password: "
$git_password = STDIN.noecho(&:gets).chomp
puts ""

git_askpass_file = "/usr/local/bin/.git_askpass.#{$git_username}"

$git_askpass_script = "#!/bin/ksh\necho \$GIT_PASSWORD\n"
File.open(git_askpass_file, 'w') { |f| f.write($git_askpass_script) }
File.chmod(0755, git_askpass_file)

ENV['GIT_PASSWORD'] = $git_password
ENV['GIT_ASKPASS'] = "#{git_askpass_file}"

###Processing starts here###
File.open($puppet_environment + "/environment.conf", 'w') { |f| f.write($environment_conf_contents) }
File.open($puppet_environment + "/manifests/site.pp", 'w') { |f| f.write($site_pp_contents) }

puts "======================================================================="
puts blue("INFO: All inputs are validated. Creating the environment. Please wait!!")
puts "======================================================================="

$puppetfile_contents.each_line do |line|
   if parts = line.match(/^mod\s+'(?<module>.*)',\s+:git\s+=>\s+'(?<repo>.*)',\s+:branch\s+=>\s+'(?<branch>.*)'/)
      git_repo_lines = true
      puppet_module = parts['module']
      repo = parts['repo']
      branch = parts['branch'] 

      repo.sub!(/ssh:/, "https:")
      repo.sub!(/git@/, $git_username + "@")
      repo.sub!(/-ssh/, "")
      repo.sub!(/:7999\//, "/scm/")
      command = $git_bin + " clone -b " + branch + " " + repo + " " + $puppet_environment + "/modules/" + puppet_module
      puts "Running: " + command
      `#{command}` 
      command = $git_bin + " --git-dir=" + $puppet_environment + "/modules/" + puppet_module + '/.git config user.name "' + $user_fullname + '"'
      puts "Running: " + command
      `#{command}` 
      command = $git_bin + " --git-dir=" + $puppet_environment + "/modules/" + puppet_module + '/.git config user.email "' + $user_email + '"'
      puts "Running: " + command
      `#{command}` 
   end
   if parts = line.match(/^mod\s+'(?<module>.*)',\s+:git\s+=>\s+'(?<repo>.*)',\s+:commit\s+=>\s+'(?<commit>.*)'/)
      git_repo_lines = true
      puppet_module = parts['module']
      repo = parts['repo']
      commit = parts['commit'] 

      repo.sub!(/ssh:/, "https:")
      repo.sub!(/git@/, $git_username + "@")
      repo.sub!(/-ssh/, "")
      repo.sub!(/:7999\//, "/scm/")
      command = $git_bin + " clone " + repo + " " + $puppet_environment + "/modules/" + puppet_module
      puts "Running: " + command
      `#{command}` 
      command = $git_bin + " --git-dir=" + $puppet_environment + "/modules/" + puppet_module + '/.git config user.name "' + $user_fullname + '"'
      puts "Running: " + command
      `#{command}` 
      command = $git_bin + " --git-dir=" + $puppet_environment + "/modules/" + puppet_module + '/.git config user.email "' + $user_email + '"'
      puts "Running: " + command
      `#{command}` 
      Dir.chdir($puppet_environment + "/modules/" + puppet_module) do
         command = $git_bin + " checkout " + commit
         puts "Running: " + command
         `#{command}`
      end
   end
end

if git_repo_lines == false
  puts red("WARNING:No GIT repo modules found.Standard Environment is created!")
end
clear_all_vars
puts "==============================================================================="
puts blue("INFO: Setup completed.Env created under #{$puppet_environment}")
puts "==============================================================================="
