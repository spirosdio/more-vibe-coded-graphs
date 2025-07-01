import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import re

# Load the uploaded CSV file
file_path = "./[2024]Έρευνα Μισθός Προγραμματιστή (Responses) - Main.csv"
df = pd.read_csv(file_path)

# --- Configuration ---
lang_col = '[NORMALIZED] Με ποιες γλώσσες προγραμματισμού δουλεύεις επαγγελματικά αυτή την περίοδο;'
salary_col = '[Fixed] Ποιος είναι ο ΕΤΗΣΙΟΣ ΚΑΘΑΡΟΣ μισθός σου σε €;'
exp_group_col = '[GROUP] Πόσα χρόνια δουλεύεις επαγγελματικά ως προγραμματιστής;'
location_col = '[GROUP] Σε ποια πόλη δουλεύεις, Greece ή Abroad'

# --- Filter for all desired languages ---
languages_to_analyze = ['Go', 'C#', 'Python', 'Rust']
regex_pattern = r'\b(' + '|'.join(languages_to_analyze) + r')\b'
# The main dataframe containing all developers for the selected languages
filtered_df = df[df[lang_col].str.contains(regex_pattern, case=False, na=False)]

# --- Create separate dataframes for each language ---
go_devs = df[df[lang_col].str.contains(r'\bGo\b', case=False, na=False)]
csharp_devs = df[df[lang_col].str.contains(r'C#', case=False, na=False)] # Keep the fix for C#
python_devs = df[df[lang_col].str.contains(r'\bPython\b', case=False, na=False)]
rust_devs = df[df[lang_col].str.contains(r'\bRust\b', case=False, na=False)]


# --- Plotting Functions ---
def plot_median_salary(data, title, filename):
    if data.empty:
        print(f"Skipping '{title}' plot because of empty dataframe.")
        return
    grouped = data.groupby([exp_group_col, location_col])[salary_col].median().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=grouped, x=exp_group_col, y=salary_col, hue=location_col)
    plt.title(title)
    plt.ylabel("Median Net Annual Salary (€)")
    plt.xlabel("Years of Experience Group")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_monthly_salary_sorted(data, title, filename):
    if data.empty:
        print(f"Skipping '{title}' plot because of empty dataframe.")
        return
    plot_data = data.copy()
    plot_data['monthly_salary'] = plot_data[salary_col] / 14

    # Sort experience groups numerically
    exp_order = sorted(plot_data[exp_group_col].dropna().unique(), key=lambda x: int(re.search(r'\d+', x).group()))
    plot_data[exp_group_col] = pd.Categorical(plot_data[exp_group_col], categories=exp_order, ordered=True)

    grouped = plot_data.groupby([exp_group_col, location_col], observed=True)['monthly_salary'].median().reset_index()

    plt.figure(figsize=(12, 7))
    barplot = sns.barplot(data=grouped, x=exp_group_col, y='monthly_salary', hue=location_col)

    for p in barplot.patches:
        barplot.annotate(format(p.get_height(), '.0f'),
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha = 'center', va = 'center', xytext = (0, 9), textcoords = 'offset points')

    plt.title(title)
    plt.ylabel("Median Net Monthly Salary (€)")
    plt.xlabel("Years of Experience Group")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# --- Generate all plots ---
dev_groups = {
    "Go": go_devs,
    "C#": csharp_devs,
    "Python": python_devs,
    "Rust": rust_devs
}

for lang, data in dev_groups.items():
    print(f"--- Processing {lang} developers ({len(data)} found) ---")
    plot_median_salary(data, f"Median Salary by Experience ({lang} Developers) - Greece vs Abroad", f"{lang.lower()}_developers_salary.png")
    plot_monthly_salary_sorted(data, f"Median Monthly Salary by Experience ({lang} Developers) - Greece vs Abroad", f"{lang.lower()}_developers_monthly_salary.png")

# --- Pairplot for all languages ---
def assign_lang(text):
    text = str(text)
    # Order matters if a developer knows multiple of these languages
    if bool(re.search(r'\bRust\b', text, re.IGNORECASE)): return 'Rust'
    if bool(re.search(r'\bGo\b', text, re.IGNORECASE)): return 'Go'
    if bool(re.search(r'C#', text, re.IGNORECASE)): return 'C#'
    if bool(re.search(r'\bPython\b', text, re.IGNORECASE)): return 'Python'
    return None

pairplot_df = filtered_df.copy()
pairplot_df['Main_Lang'] = pairplot_df[lang_col].apply(assign_lang)
pairplot_df = pairplot_df[[salary_col, exp_group_col, location_col, 'Main_Lang']].dropna()

if not pairplot_df.empty:
    print("--- Generating pairplot for all selected languages ---")
    plt.figure()
    pairplot = sns.pairplot(pairplot_df, hue='Main_Lang', hue_order=languages_to_analyze)
    pairplot.fig.suptitle("Pairplot for Go, C#, Python, and Rust Developers", y=1.02)
    plt.savefig("pairplot_all_languages.png")
    plt.close()
else:
    print("Skipping pairplot because of empty dataframe.")
