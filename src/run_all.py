import os
import subprocess
import sys

def run_all_scripts():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_exec = sys.executable
    src_dir = os.path.join(base_dir, "src")

    scripts = [
        "01_data_preparation.py",
        "02_create_database.py",
        "03_eda_analysis.py",
        "04_abc_xyz_analysis.py",
        "05_forecasting.py",
        "06_inventory_planning.py",
        "07_generate_excel_workbook.py",
        "test_sql_queries.py"
    ]

    print("=" * 70)
    print("RUNNING END-TO-END REPRODUCIBILITY TEST")
    print("=" * 70)

    for script in scripts:
        script_path = os.path.join(src_dir, script)
        print(f"\n---> Executing: {script}")
        res = subprocess.run([py_exec, script_path], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [OK] {script} finished successfully.")
            # Print last few lines of stdout
            lines = res.stdout.strip().splitlines()
            for l in lines[-3:]:
                print(f"       {l}")
        else:
            print(f"  [ERROR] {script} failed with return code {res.returncode}")
            print(res.stderr)
            sys.exit(1)

    print("\n" + "=" * 70)
    print("ALL SCRIPTS EXECUTED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 70)

if __name__ == '__main__':
    run_all_scripts()
