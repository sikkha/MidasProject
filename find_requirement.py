import os
import re
import pkgutil

def is_standard_lib(module):
    """Check if a module is part of the standard library."""
    return module in std_lib_modules

def find_imports(file_path):
    """Extract imported modules from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        # Regex to find module names in import statements
        pattern = re.compile(r'^\s*(from\s+([\w\.]+)|import\s+([\w\.]+))', re.MULTILINE)
        imports = set(match[1] or match[2] for match in pattern.findall(file_content))
        return imports

def generate_requirements(directory):
    """Generate a requirements.txt file from imports in all Python files in the directory."""
    all_imports = set()
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(subdir, file)
                imports = find_imports(file_path)
                all_imports.update(imports)

    # Filter out standard library modules
    non_std_lib_imports = {imp for imp in all_imports if not is_standard_lib(imp.split('.')[0])}
    
    # Write to requirements.txt
    with open('requirements.txt', 'w') as req_file:
        for imp in sorted(non_std_lib_imports):
            req_file.write(imp + '\n')

    print("requirements.txt has been generated.")

if __name__ == "__main__":
    # Preload standard library module names
    std_lib_modules = {mod.name for mod in pkgutil.iter_modules()}
    
    # Use the current directory or specify any directory you want to scan
    generate_requirements('.')

