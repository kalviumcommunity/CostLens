import sys

def main():
    print("Cloud Cost Intelligence Platform")
    
    # Simple dependency verification checks
    dependencies = [
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "plotly",
        "streamlit",
        "sqlalchemy",
        "sklearn"
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
            
    if not missing_deps:
        print("Environment configured successfully")
    else:
        print(f"Warning: The following dependencies are missing: {', '.join(missing_deps)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
