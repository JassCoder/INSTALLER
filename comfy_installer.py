import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

LOG_FILE = "installer_log.txt"


def log(text):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {text}\n")


def check_tool(tool_name, command):
    try:
        subprocess.check_call(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except:
        return False


def pick_custom_nodes():
    folder = filedialog.askdirectory(title="Select your custom_nodes folder")
    if folder:
        if folder.endswith("custom_nodes"):
            custom_nodes_var.set(folder)
        else:
            messagebox.showerror("Invalid Folder", "This is NOT a custom_nodes folder.")
            custom_nodes_var.set("")


def run_cmd(cmd, cwd=None):
    try:
        log(f"RUN: {cmd}")
        subprocess.check_call(cmd, shell=True, cwd=cwd)
        return True
    except Exception as e:
        log(f"ERROR: {e}")
        return False


def install_repo():
    custom_nodes = custom_nodes_var.get().strip()
    repo_url = repo_var.get().strip()

    if not custom_nodes:
        messagebox.showerror("Error", "Select your custom_nodes folder first.")
        return

    if not os.path.isdir(custom_nodes):
        messagebox.showerror("Error", "custom_nodes folder does not exist.")
        return

    if not custom_nodes.endswith("custom_nodes"):
        messagebox.showerror("Error", "You must select the custom_nodes folder.")
        return

    if not repo_url.startswith("https://github.com/"):
        messagebox.showerror("Error", "Enter a valid GitHub repository URL.")
        return

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    dest = os.path.join(custom_nodes, repo_name)

    # Skip clone if folder exists
    if os.path.exists(dest):
        messagebox.showinfo(
            "Skipping",
            f"Repository already exists:\n{dest}\nSkipping clone...",
        )
        log(f"SKIPPED clone: {dest} already present")
    else:
        messagebox.showinfo("Installing", f"Cloning repo:\n{repo_url}")
        if not run_cmd(f'git clone "{repo_url}" "{dest}"'):
            messagebox.showerror("Error", "Failed to clone repository. Check log.")
            return

    # Check requirements
    req_path = os.path.join(dest, "requirements.txt")

    if not os.path.isfile(req_path):
        messagebox.showinfo("Done", "Repository installed. No requirements.txt found.")
        return

    messagebox.showinfo("Checking", "Found requirements.txt\nChecking packages...")

    with open(req_path, "r") as f:
        requirements = [line.strip() for line in f if line.strip()]

    missing = []

    # Detect missing modules
    for req in requirements:
        pkg = req.split("==")[0].strip()
        test_import = pkg.replace("-", "_")
        try:
            subprocess.check_call(
                f'python -c "import {test_import}"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except:
            missing.append(req)

    if not missing:
        messagebox.showinfo("Done", "All requirements already installed.")
        log("SKIPPED requirements: all satisfied")
        return

    # Install missing packages
    messagebox.showinfo("Installing", "Installing missing dependencies...")

    req_temp = "temp_requirements.txt"
    with open(req_temp, "w") as f:
        f.write("\n".join(missing))

    if not run_cmd(f'python -m pip install -r "{req_temp}"'):
        messagebox.showerror("Error", "Failed installing some requirements.")
        log("ERROR installing missing requirements")
        return

    os.remove(req_temp)
    messagebox.showinfo("Done", "Repository + missing requirements installed successfully.")


def verify_tools():
    python_ok = check_tool("python", "python --version")
    git_ok = check_tool("git", "git --version")

    if python_ok and git_ok:
        messagebox.showinfo("Ready", "Python and Git are installed.")
    else:
        msg = ""
        if not python_ok:
            msg += "Python NOT installed.\n"
        if not git_ok:
            msg += "Git NOT installed.\n"
        messagebox.showerror("Missing Tools", msg)


# GUI
root = tk.Tk()
root.title("ComfyUI Repo Installer")
root.geometry("520x330")
root.resizable(False, False)

tk.Label(root, text="custom_nodes Folder:", font=("Arial", 11)).pack(pady=5)
custom_nodes_var = tk.StringVar()
tk.Entry(root, textvariable=custom_nodes_var, width=55).pack()
tk.Button(root, text="Browse", command=pick_custom_nodes).pack(pady=5)

tk.Label(root, text="GitHub Repository URL:", font=("Arial", 11)).pack(pady=10)
repo_var = tk.StringVar()
tk.Entry(root, textvariable=repo_var, width=55).pack()

tk.Button(root, text="Install Repository", width=22, command=install_repo).pack(pady=15)
tk.Button(root, text="Verify Tools", width=22, command=verify_tools).pack(pady=5)

tk.Label(root, text="Logs saved to installer_log.txt", font=("Arial", 9)).pack(pady=5)
tk.Label(root, text="Try not to break this one, Jas.", font=("Arial", 9)).pack(pady=10)

root.mainloop()
