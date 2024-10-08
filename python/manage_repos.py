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

# Protected branches that should not be deleted
protected_branches = ['develop', 'master']

def clone_repo(repo_url, clone_dir):
    try:
        print(f'Cloning repository {repo_url} into {clone_dir}')
        git.Repo.clone_from(repo_url, clone_dir)
    except Exception as e:
        print(f'Failed to clone {repo_url}: {e}')

def fetch_all_branches(repo):
    """
    Fetch all branches from the remote to ensure that we can operate on them.
    """
    print(f"Fetching branches from remote for {repo.working_tree_dir}")
    repo.git.fetch('--all')  # Fetch all branches from remote
    repo.git.fetch('--prune')  # Remove any deleted remote branches

def list_all_branches(repo):
    """
    List both local and remote branches, marking protected branches.
    """
    print("Local branches:")
    for branch in repo.branches:
        branch_name = branch.name
        if branch_name in protected_branches:
            print(f"{branch_name} (protected)")
        else:
            print(branch_name)

    print("\nRemote branches:")
    for ref in repo.remote().refs:
        branch_name = ref.name.split('/')[-1]  # Extract branch name from remote ref
        if branch_name in protected_branches:
            print(f"{branch_name} (protected)")
        else:
            print(branch_name)

def list_merged_branches(repo):
    """
    List merged branches, including both local and remote branches.
    """
    default_branch = repo.active_branch.name
    print(f"Listing merged branches into {default_branch} (local and remote):")

    # Fetch latest branches from remote
    fetch_all_branches(repo)

    merged_branches = repo.git.branch('-r', '--merged', default_branch).splitlines()
    for branch in merged_branches:
        print(branch.strip())

def list_unmerged_branches(repo):
    """
    List unmerged branches, including both local and remote branches.
    """
    default_branch = repo.active_branch.name
    print(f"Listing unmerged branches from {default_branch} (local and remote):")

    # Fetch latest branches from remote
    fetch_all_branches(repo)

    unmerged_branches = repo.git.branch('-r', '--no-merged', default_branch).splitlines()
    for branch in unmerged_branches:
        print(branch.strip())

def create_branch(repo, branch_name):
    try:
        repo.git.branch(branch_name)
        print(f'Branch {branch_name} created successfully')
    except Exception as e:
        print(f'Failed to create branch {branch_name}: {e}')

def delete_branch(repo, branch_name):
    """
    Delete a branch after checking if it's protected.
    """
    if branch_name in protected_branches:
        print(f"Error: Branch '{branch_name}' is protected and cannot be deleted.")
        return

    try:
        repo.git.branch('-D', branch_name)
        print(f'Branch {branch_name} deleted successfully')
    except Exception as e:
        print(f'Failed to delete branch {branch_name}: {e}')

def delete_merged_branches(repo):
    """
    Delete merged branches, ensuring that protected branches are not deleted.
    """
    try:
        default_branch = repo.active_branch.name
        print(f'Deleting merged branches into {default_branch} (local and remote):')

        # Fetch latest branches from remote
        fetch_all_branches(repo)

        # Get list of merged branches
        merged_branches = repo.git.branch('-r', '--merged', default_branch).splitlines()

        for branch in merged_branches:
            branch_name = branch.strip().split('/')[-1]  # Extract branch name
            if branch_name not in protected_branches:
                print(f'Deleting merged branch: {branch_name}')
                repo.git.push('origin', '--delete', branch_name)
            else:
                print(f'Skipping protected branch: {branch_name}')
    except Exception as e:
        print(f'Failed to delete merged branches in {repo.working_tree_dir}: {e}')

def delete_all_branches(repo):
    """
    Delete all branches except for protected ones.
    """
    try:
        default_branch = repo.active_branch.name
        print(f'Deleting all branches except {default_branch} and protected branches (local and remote):')

        # Fetch latest branches from remote
        fetch_all_branches(repo)

        all_branches = repo.git.branch('-r').splitlines()
        all_branches = [branch.strip().split('/')[-1] for branch in all_branches]  # Get branch names

        for branch in all_branches:
            if branch not in protected_branches and branch != default_branch:
                print(f'Deleting branch: {branch}')
                repo.git.push('origin', '--delete', branch)
            else:
                print(f'Skipping protected or default branch: {branch}')

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

        # Fetch all remote branches before proceeding
        fetch_all_branches(repo)

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
