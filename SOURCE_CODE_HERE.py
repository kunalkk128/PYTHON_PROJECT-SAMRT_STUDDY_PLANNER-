import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Files to save data permanently
PLAN_FILE = "study_plan.csv"
LOG_FILE = "daily_logs.csv"

# 1. Check or Create CSV Files
if not os.path.exists(PLAN_FILE):
    pd.DataFrame(columns=["Subject", "Total_Target_Hours"]).to_csv(PLAN_FILE, index=False)

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Date", "Subject", "Hours_Done"]).to_csv(LOG_FILE, index=False)


# --- MAIN GUI APP ---
root = tk.Tk()
root.title("📚 Smart Study Planner & Tracker")
root.geometry("650x600")
root.configure(bg="#f0f4f8")

# Create Tabs System
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True, fill="both")

tab_plan = tk.Frame(notebook, bg="#ffffff")
tab_log = tk.Frame(notebook, bg="#ffffff")

notebook.add(tab_plan, text=" 📌 Step 1: Set Study Plan ")
notebook.add(tab_log, text=" 📝 Step 2: Daily Log & Analytics ")


# ==========================================
# TAB 1: STUDY PLAN SETUP (ONE TIME SETUP)
# ==========================================

def save_plan():
    sub = entry_plan_sub.get().strip()
    hrs = entry_plan_hrs.get().strip()

    if sub == "" or hrs == "":
        messagebox.showwarning("Warning", "Subject aur Target Hours bharo!")
        return

    try:
        hrs_val = float(hrs)
    except ValueError:
        messagebox.showerror("Error", "Hours me number daalo!")
        return

    # Read existing plan, add new subject, and save
    df_plan = pd.read_csv(PLAN_FILE)
    
    # Check if subject already exists
    if sub in df_plan["Subject"].values:
        messagebox.showinfo("Info", f"{sub} pehle se added hai!")
        return

    new_row = pd.DataFrame([{"Subject": sub, "Total_Target_Hours": hrs_val}])
    df_plan = pd.concat([df_plan, new_row], ignore_index=True)
    df_plan.to_csv(PLAN_FILE, index=False)

    entry_plan_sub.delete(0, tk.END)
    entry_plan_hrs.delete(0, tk.END)

    update_plan_table()
    update_subject_dropdown()
    messagebox.showinfo("Success", f"{sub} Plan me add ho gaya!")

def update_plan_table():
    for item in tree_plan.get_children():
        tree_plan.delete(item)
    df_plan = pd.read_csv(PLAN_FILE)
    for idx, row in df_plan.iterrows():
        tree_plan.insert("", "end", values=(row["Subject"], row["Total_Target_Hours"]))

# Tab 1 UI Elements
tk.Label(tab_plan, text="🎯 Set Target Study Hours per Subject", font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=10)

frame_plan_inputs = tk.Frame(tab_plan, bg="#ffffff")
frame_plan_inputs.pack(pady=5)

tk.Label(frame_plan_inputs, text="Subject:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
entry_plan_sub = tk.Entry(frame_plan_inputs, width=15)
entry_plan_sub.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_plan_inputs, text="Target Hours:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
entry_plan_hrs = tk.Entry(frame_plan_inputs, width=10)
entry_plan_hrs.grid(row=0, column=3, padx=5, pady=5)

btn_plan_save = tk.Button(tab_plan, text="Add to Target Plan", command=save_plan, bg="#27ae60", fg="white", font=("Arial", 9, "bold"))
btn_plan_save.pack(pady=5)

tree_plan = ttk.Treeview(tab_plan, columns=("Subject", "Target"), show="headings", height=8)
tree_plan.heading("Subject", text="Planned Subject")
tree_plan.heading("Target", text="Total Target (Hours)")
tree_plan.column("Subject", width=200, anchor="center")
tree_plan.column("Target", width=150, anchor="center")
tree_plan.pack(pady=10, padx=20, fill="both")


# ==========================================
# TAB 2: DAILY LOG & MATPLOTLIB ANALYTICS
# ==========================================

def update_subject_dropdown():
    df_plan = pd.read_csv(PLAN_FILE)
    subjects = df_plan["Subject"].tolist()
    combo_log_sub['values'] = subjects
    if subjects:
        combo_log_sub.current(0)

def save_daily_log():
    sub = combo_log_sub.get()
    hrs = entry_log_hrs.get().strip()
    date_val = entry_log_date.get().strip()

    if sub == "" or hrs == "" or date_val == "":
        messagebox.showwarning("Warning", "All fields Fill is Compalsary!")
        return

    try:
        hrs_val = float(hrs)
    except ValueError:
        messagebox.showerror("Error", "FILL THE NUMBER IN HRS!")
        return

    df_log = pd.read_csv(LOG_FILE)
    new_log = pd.DataFrame([{"Date": date_val, "Subject": sub, "Hours_Done": hrs_val}])
    df_log = pd.concat([df_log, new_log], ignore_index=True)
    df_log.to_csv(LOG_FILE, index=False)

    entry_log_hrs.delete(0, tk.END)
    update_log_table()
    messagebox.showinfo("Saved", "Daily log CSV SAVED!")

def update_log_table():
    for item in tree_log.get_children():
        tree_log.delete(item)
    df_log = pd.read_csv(LOG_FILE)
    for idx, row in df_log.iterrows():
        tree_log.insert("", "end", values=(row["Date"], row["Subject"], row["Hours_Done"]))

def show_analytics_chart():
    df_plan = pd.read_csv(PLAN_FILE)
    df_log = pd.read_csv(LOG_FILE)

    if df_plan.empty:
        messagebox.showwarning("No Data", "Pehle Step 1 me Plan add karo!")
        return

    # Grouping logged hours by Subject using Pandas & NumPy
    if df_log.empty:
        completed_hours = {sub: 0 for sub in df_plan["Subject"]}
    else:
        log_grouped = df_log.groupby("Subject")["Hours_Done"].sum().to_dict()
        completed_hours = {sub: log_grouped.get(sub, 0) for sub in df_plan["Subject"]}

    subjects = df_plan["Subject"].tolist()
    targets = df_plan["Total_Target_Hours"].tolist()
    dones = [completed_hours[sub] for sub in subjects]

    # Matplotlib Chart Setup
# Dark Cyberpunk Style Setup
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7.5, 4.8), facecolor='#0d1117')
    ax.set_facecolor('#161b22')

    x = np.arange(len(subjects))

    # 1. Target Line + Glowing Dots (Neon Purple)
    ax.stem(x - 0.15, targets, linefmt='#a855f7', markerfmt='o', basefmt=" ", label='Target Planned (Hrs)')
    
    # 2. Completed Line + Glowing Dots (Neon Yellow/Lime)
    ax.stem(x + 0.15, dones, linefmt='#eab308', markerfmt='D', basefmt=" ", label='Actual Completed (Hrs)')

    # Values on top of dots
    for i in range(len(subjects)):
        ax.text(x[i] - 0.15, targets[i] + 0.3, str(targets[i]), color='#c084fc', fontweight='bold', fontsize=9, ha='center')
        ax.text(x[i] + 0.15, dones[i] + 0.3, str(dones[i]), color='#fde047', fontweight='bold', fontsize=9, ha='center')

    # Styling Labels & Titles
    ax.set_xlabel('Subjects', color="#d4b60a", fontweight='bold', fontsize=10)
    ax.set_ylabel('Hours', color="#d6d908", fontweight='bold', fontsize=10)
    ax.set_title('⚡ SMART STUDY PLANNER: TARGET VS ACTUAL ⚡', color='white', fontweight='bold', fontsize=12)
    
    ax.set_xticks(x)
    ax.set_xticklabels(subjects, color='white', fontweight='bold')
    
    ax.legend(facecolor='#0d1117', edgecolor="#c4d10d", labelcolor='white')
    ax.grid(color='#30363d', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.show()

# Tab 2 UI Elements
tk.Label(tab_log, text="📝 Log Daily Completed Study Hours", font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=10)

frame_log_inputs = tk.Frame(tab_log, bg="#ffffff")
frame_log_inputs.pack(pady=5)

tk.Label(frame_log_inputs, text="Date/Day:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
entry_log_date = tk.Entry(frame_log_inputs, width=10)
entry_log_date.insert(0, "Day 1")
entry_log_date.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_log_inputs, text="Subject:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
combo_log_sub = ttk.Combobox(frame_log_inputs, width=12, state="readonly")
combo_log_sub.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_log_inputs, text="Hours Done:", bg="#ffffff").grid(row=0, column=4, padx=5, pady=5)
entry_log_hrs = tk.Entry(frame_log_inputs, width=8)
entry_log_hrs.grid(row=0, column=5, padx=5, pady=5)

btn_log_save = tk.Button(tab_log, text="Save Daily Log", command=save_daily_log, bg="#2980b9", fg="white", font=("Arial", 9, "bold"))
btn_log_save.pack(pady=5)

btn_chart = tk.Button(tab_log, text="Show Planned vs Actual Progress Chart 📊", command=show_analytics_chart, bg="#8e44ad", fg="white", font=("Arial", 10, "bold"))
btn_chart.pack(pady=5)

tree_log = ttk.Treeview(tab_log, columns=("Date", "Subject", "Hours"), show="headings", height=6)
tree_log.heading("Date", text="Date / Day")
tree_log.heading("Subject", text="Subject")
tree_log.heading("Hours", text="Hours Completed")
tree_log.column("Date", width=100, anchor="center")
tree_log.column("Subject", width=150, anchor="center")
tree_log.column("Hours", width=120, anchor="center")
tree_log.pack(pady=10, padx=20, fill="both")

# Initialize Tables and Dropdowns
update_plan_table()
update_subject_dropdown()
update_log_table()

root.mainloop()