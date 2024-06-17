import os
import git

# List of Bitbucket repository URLs (clone URLs)
repos = [
    'git@bitbucket.org:your_username/repo1.git',
    'git@bitbucket.org:your_username/repo2.git',
    # Add more repositories as needed
]

# Directory where repositories will be cloned
base_dir = '/path/to/clone/repositories'  # Change this to your desired directory

# Ensure the base directory exists
os.makedirs(base_dir, exist_ok=True)

def clone_repo(repo_url, clone_dir):
    try:
        print(f'Cloning repository {repo_url} into {clone_dir}')
        git.Repo.clone_from(repo_url, clone_dir)
    except Exception as e:
        print(f'Failed to clone {repo_url}: {e}')

def list_all_branches(repo):
    print("All branches:")
    for branch in repo.branches:
        print(branch)

def list_merged_branches(repo):
    print("Merged branches:")
    merged_branches = repo.git.branch('--merged').split()
    for branch in merged_branches:
        print(branch.strip())

def list_unmerged_branches(repo):
    print("Unmerged branches:")
    unmerged_branches = repo.git.branch('--no-merged').split()
    for branch in unmerged_branches:
        print(branch.strip())

def create_branch(repo, branch_name):
    try:
        repo.git.branch(branch_name)
        print(f'Branch {branch_name} created successfully')
    except Exception as e:
        print(f'Failed to create branch {branch_name}: {e}')

def delete_branch(repo, branch_name):
    try:
        repo.git.branch('-D', branch_name)
        print(f'Branch {branch_name} deleted successfully')
    except Exception as e:
        print(f'Failed to delete branch {branch_name}: {e}')

def delete_merged_branches(repo):
    try:
        default_branch = repo.active_branch.name
        print(f'Default branch is {default_branch}')

        # Get list of merged branches
        merged_branches = repo.git.branch('--merged').split()
        merged_branches = [branch.strip() for branch in merged_branches]

        # Delete merged branches
        for branch in merged_branches:
            if branch != default_branch and not branch.startswith('*'):
                print(f'Deleting merged branch: {branch}')
                repo.git.branch('-d', branch)
            else:
                print(f'Skipping branch: {branch}')

    except Exception as e:
        print(f'Failed to delete merged branches in {repo.working_tree_dir}: {e}')

def delete_all_branches(repo):
    try:
        default_branch = repo.active_branch.name
        print(f'Default branch is {default_branch}')
        
        all_branches = repo.git.branch().split()
        all_branches = [branch.strip() for branch in all_branches]

        for branch in all_branches:
            if branch != default_branch and not branch.startswith('*'):
                print(f'Deleting branch: {branch}')
                repo.git.branch('-D', branch)
            else:
                print(f'Skipping branch: {branch}')
                
    except Exception as e:
        print(f'Failed to delete branches in {repo.working_tree_dir}: {e}')

def show_menu():
    print("\nMenu:")
    print("1. List all branches")
    print("2. List merged branches")
    print("3. List unmerged branches")
    print("4. Create a branch")
    print("5. Delete a branch")
    print("6. Delete merged branches")
    print("7. Delete all branches")
    print("8. Quit")

def main():
    for repo_url in repos:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        clone_dir = os.path.join(base_dir, repo_name)

        if not os.path.exists(clone_dir):
            clone_repo(repo_url, clone_dir)

        repo = git.Repo(clone_dir)

        while True:
            show_menu()
            choice = input("Enter your choice: ")

            if choice == '1':
                list_all_branches(repo)
            elif choice == '2':
                list_merged_branches(repo)
            elif choice == '3':
                list_unmerged_branches(repo)
            elif choice == '4':
                branch_name = input("Enter the branch name to create: ")
                create_branch(repo, branch_name)
            elif choice == '5':
                branch_name = input("Enter the branch name to delete: ")
                delete_branch(repo, branch_name)
            elif choice == '6':
                delete_merged_branches(repo)
            elif choice == '7':
                delete_all_branches(repo)
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
