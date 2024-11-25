import os
from pathlib import Path

class ProjectSetup:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.structure = {
            'core': ['models', 'api', 'security'],
            'interfaces': ['cli/commands', 'gui/components', 'gui/pages'],
            'utils': ['cache', 'docs', 'history'],
            'tests': ['unit', 'integration', 'performance'],
            'config': [],
            'scripts': [],
            'docker': [],
            '.github/workflows': [],
            'docs': ['api', 'guides']
        }

    def create_structure(self):
        for dir_path, subdirs in self.structure.items():
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            if 'tests' not in str(full_path):
                (full_path / '__init__.py').touch()
            
            for subdir in subdirs:
                subdir_path = full_path / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)
                if 'tests' not in str(subdir_path):
                    (subdir_path / '__init__.py').touch()

def main():
    setup = ProjectSetup('.')
    setup.create_structure()

if __name__ == "__main__":
    main()