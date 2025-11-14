import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def select_custom_nodes():
    folder = filedialog.askdirectory(title="Select custom_nodes Folder")
    if folder:
        custom_nodes_var.set(folder)

def run(cmd, cwd=None):
    try:
        subprocess.check_call(cmd, shell=True, cwd=cwd)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def install_repo():
    custom_nodes = custom_nodes_var.get().strip()
    repo_url = repo_var.get().strip()

    if not custom_nodes:
        messagebox.showerror("Error", "Select your custom_nodes folder.")
        return

    if not repo_url:
        messagebox.showerror("Error", "Enter a valid repo URL.")
        return

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    dest_path = os.path.join(custom_nodes, repo_name)

    messagebox.showinfo("Installing", f"Cloning:\n{repo_url}\n\nto:\n{dest_path}")

    if not run(f'git clone "{repo_url}" "{dest_path}"'):
        messagebox.showerror("Error", "Failed cloning repository.")
        return

    # Install requirements.txt if present
    req_path = os.path.join(dest_path, "requirements.txt")
    if os.path.isfile(req_path):
        messagebox.showinfo("Installing Requirements", f"Installing dependencies for {repo_name}...")

        # FIXED: use python -m pip instead of pip
        if run(f'python -m pip install -r "{req_path}"'):
            messagebox.showinfo("Success", "Requirements installed successfully.")
        else:
            messagebox.showerror("Error", "Failed installing requirements.")
            return
    else:
        messagebox.showinfo("Info", "No requirements.txt found.")

    messagebox.showinfo("Done", f"{repo_name} installed successfully.")

# GUI SETUP
root = tk.Tk()
root.title("ComfyUI Repo Installer")
root.geometry("520x300")
root.resizable(False, False)

tk.Label(root, text="custom_nodes Folder Path:", font=("Arial", 11)).pack(pady=5)
custom_nodes_var = tk.StringVar()
tk.Entry(root, textvariable=custom_nodes_var, width=55).pack()
tk.Button(root, text="Browse", command=select_custom_nodes).pack(pady=5)

tk.Label(root, text="GitHub Repo URL:", font=("Arial", 11)).pack(pady=10)
repo_var = tk.StringVar()
tk.Entry(root, textvariable=repo_var, width=55).pack()

tk.Button(root, text="Install Repository", width=22, command=install_repo).pack(pady=15)

tk.Label(root, text="Jas… now pip won't complain anymore.", font=("Arial", 9)).pack(pady=20)

root.mainloop()
