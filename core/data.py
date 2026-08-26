import requests
import json
from contextlib import redirect_stdout 


#  DeepSWE https://deepswe.datacurve.ai/  
HTML_JSON_URL = "https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json"

 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
}


# Забирает JSON с даными. / Fetches JSON with data.
def load_rows():
    try:
        response = requests.get(HTML_JSON_URL, headers=HEADERS, timeout=10)
        data = response.json()
        return data["rows"]
    except Exception as e:
        print(f"[☓] Failed to load data: {e}")
        return None


# Оставляет от каждой модели лучший pass_rate и сортирует по убыванию. / Keeps the best pass_rate for each model and sorts in descending order.
def build_leaderboard(rows):
    best_models = {}

    for row in rows:
        model = row["model"]

        if model not in best_models:
            best_models[model] = row

        elif row["pass_rate"] > best_models[model]["pass_rate"]:
            best_models[model] = row

    return sorted(
        best_models.values(),
        key=lambda x: x["pass_rate"],
        reverse=True
    )

    
# 1 Забирает JSON с рейтингом моделей и красиво его выводит. / Fetches the JSON containing model ratings and displays it in a nicely formatted way.
def show_leaderboard():
    rows = load_rows()
    if rows is None:
        return

    for position_id, row in enumerate(build_leaderboard(rows), start=1):
        effort = row["reasoning_effort"]
        pass_rate = row["pass_rate"] * 100
        effort_text = f"[{effort}]" if effort is not None else ""

        print(
            f"{position_id:3}.  "
            f"{row['model']:<28}"
            f"{effort_text:<12}"
            f" {pass_rate:6.2f}%"
        )


# 2 Выводит топ-3 моделей с медалями, score. / Outputs the top 3 models with medals and scores. 
def top_power():
    rows = load_rows()
    if rows is None:
        return

    leaderboard = build_leaderboard(rows)
    medals = ["1️⃣ ", "2️⃣ ", "3️⃣ ", "4️⃣ ", "5️⃣ "]

    for position_id, row in enumerate(leaderboard[:5]):
        print(f"""
 {medals[position_id]}  {row['model']}
      Score : {row['pass_rate'] * 100:.2f}%
      Cost  : ${row['mean_cost_usd']:.2f}
""")


# 3 Поиск модели. / Model search.
def search_models():
    search = input("Enter model name to search: ").strip().lower() 

    if not any(char.isalpha() for char in search):
        print("\n[!] Error: Please enter a valid model name.")
        return

    rows = load_rows()
    if rows is None:
        return
   
    leaderboard = build_leaderboard(rows)
    found_models = {}

    for row in leaderboard:
        model = row["model"]
        
        if search in model.lower():
            found_models[model] = row
        
    if not found_models:
        print("\n[!] No models found.")
        return
    
    print("\n───────────────────────────────────────────────────────────────\n")
    
    for model, row in found_models.items():
        print(f"{model:<20}  :  {row['pass_rate'] * 100:.2f}%    ${row['mean_cost_usd']:.2f}")


# 4 Сравнение моделей. / Model comparison.
def compare_models():
    model1 = input("Enter the first model name to compare: ").strip().lower()
    model2 = input("Enter the second model name to compare: ").strip().lower()

    rows = load_rows()
    if rows is None:
        return

    model1_data = next((row for row in rows if row["model"].lower() == model1), None)
    model2_data = next((row for row in rows if row["model"].lower() == model2), None)

    if not model1_data or not model2_data:
        print("\n[!] Error: One or both models not found.")
        return

    print(f"""
───────────────────────────────────────────────────────────────

COMPARISON

MODEL                    PASS RATE        COST
───────────────────────────────────────────────────────────────

{model1_data['model']:<20}     {model1_data['pass_rate'] * 100:.2f}%    ${model1_data['mean_cost_usd']:.2f}
{model2_data['model']:<20}     {model2_data['pass_rate'] * 100:.2f}%    ${model2_data['mean_cost_usd']:.2f}

───────────────────────────────────────────────────────────────

WINNER: {model1_data['model'] if model1_data['pass_rate'] > model2_data['pass_rate'] else model2_data['model']}
""")


# 5 Выводит подробную информацию о выбранной модели. / Displays detailed information about the selected model.
def model_details():
    search = input("Enter model name to search: ").strip().lower() 
    
    if not any(char.isalpha() for char in search):
        print("\n[!] Error: Please enter a valid model name.")
        return
    
    rows = load_rows()
    if rows is None:
        return

    leaderboard = build_leaderboard(rows)
    found_models = {}

    for row in leaderboard:
        model = row["model"]

        if search in model.lower():
            found_models[model] = row

    if not found_models:
        print("\n[!] No models found.")
        return
    
    print("\n───────────────────────────────────────────────────────────────\n\nMODEL INFORMATION")
        
    for model, row in found_models.items():
        effort = row["reasoning_effort"]
        effort_text = f"[{effort}]" if effort is not None else ""
        print(f"""
Model          : {model}
Reasoning      : {effort_text}
Pass Rate      : {row['pass_rate'] * 100:.2f}%
Cost           : ${row['mean_cost_usd']:.2f}
Source         : {row["source"]}
Config         : {row["config"]}
""")


# 6 Отображает статистику по моделям. / Displays statistics about the models.
def show_statistics():
    search = input("Enter the model name to search for statistics: ").strip().lower()
        
    if not any(char.isalpha() for char in search):
        print("\n[!] Error: Please enter a valid model name.")
        return
        
    rows = load_rows()
    if rows is None:
        return
    
    leaderboard = build_leaderboard(rows)
    found_models = {}
    
    for row in leaderboard:
        model = row["model"]
    
        if search in model.lower():
            found_models[model] = row
    
    if not found_models:
        print("\n[!] No models found.")
        return

    print("\n───────────────────────────────────────────────────────────────")
           
    for model, row in found_models.items():
        effort = row["reasoning_effort"]
        effort_text = f"[{effort}]" if effort is not None else ""
        print(f"""
STATISTICS

───────────────────────────────────────────────────────────────

Model              : {model}
Reasoning          : {effort_text}

PASS RATE

Pass Rate           : {row['pass_rate'] * 100:.2f}%
Pass@1              : {row['pass_at_1'] * 100:.2f}%
Pass@4              : {row['pass_at_4'] * 100:.2f}%

TASK RESULTS

Passed              : {row['n_passed']}
Attempted           : {row['n_attempted']}
Tasks Passed        : {row['n_tasks_passed_any']}
Tasks Attempted     : {row['n_tasks_attempted']}

RUNS

Runs                : {row['n_runs']}

COST

Mean Cost           : ${row['mean_cost_usd']:.2f}
Median Cost         : ${row['median_cost_usd']:.2f}

EFFICIENCY

Mean Duration       : {row['mean_duration_seconds'] / 60:.2f} min
Mean Agent Steps    : {row['mean_agent_steps']:.2f}
Mean Input Tokens   : {row['mean_input_tokens']:.0f}
Mean Output Tokens  : {row['mean_output_tokens']:.0f}

═══════════════════════════════════════════════════════════════ 
""")


# 7 Экспортирую данные из моего кода в файлы. / We are exporting data from my code to files.
def export_data():
    try:
        option = int(input("Select an option: "))
    except ValueError:
            print("\n[!] Error: Please enter a valid number from 1 to 5.")
            return

    if (option < 1) or (option > 5):
        print("\n[!] Error: Please enter a valid number from 1 to 5.")
        return
    elif option == 1:
        with open("leaderboard.txt", "w", encoding="utf-8") as file: 
            with redirect_stdout(file):  
                show_leaderboard()
        print("\nThe file has been saved.")
    elif option == 2:
        search = input("\nEnter model name to search: ").strip().lower()
               
        if not any(char.isalpha() for char in search):
            print("\n[!] Error: Please enter a valid model name.")
            return

        rows = load_rows()
        if rows is None:
            return
    
        leaderboard = build_leaderboard(rows)
        found_models = {}
    
        for row in leaderboard:
            model = row["model"]
    
            if search in model.lower():
                found_models[model] = {
                    "model": row["model"],
                    "reasoning": row["reasoning_effort"],
                    "pass_rate": row["pass_rate"],
                    "pass_at_1": row["pass_at_1"],
                    "pass_at_4": row["pass_at_4"],
                    "n_passed": row["n_passed"],
                    "n_attempted": row["n_attempted"],
                    "n_tasks_passed_any": row["n_tasks_passed_any"],
                    "n_tasks_attempted": row["n_tasks_attempted"],
                    "n_runs": row["n_runs"],
                    "mean_cost_usd": row["mean_cost_usd"],
                    "median_cost_usd": row["median_cost_usd"],
                    "mean_duration_seconds": row["mean_duration_seconds"],
                    "mean_agent_steps": row["mean_agent_steps"],
                    "mean_input_tokens": row["mean_input_tokens"],
                    "mean_output_tokens": row["mean_output_tokens"]
                }
    
        if not found_models:
            print("\n[!] No models found.")
            return

        with open("model_details.json", "w", encoding="utf-8") as file:
            json.dump(found_models, file, indent=4, ensure_ascii=False)
        print("\nThe file has been saved.")
    elif option == 3:
        search = input("\nEnter model name to search: ").strip().lower()
        
        if not any(char.isalpha() for char in search):
            print("\n[!] Error: Please enter a valid model name.")
            return
        
        rows = load_rows()  
        if rows is None:
            return
        
        found_models = {}

        for row in rows:
            model = row["model"]

            if search in model.lower():
                found_models[model] = {
                    "Model": f"{model}",
                    "Reasoning": f"{row["reasoning_effort"]}",
                    "Pass Rate": f"{row['pass_rate'] * 100:.2f}%",
                    "Cost": f"${row['mean_cost_usd']:.2f}",
                    "Source": f"{row["source"]}",
                    "Config": f"{row["config"]}"  
                }

        if not found_models:
            print("\n[!] No models found.")
            return
        
        with open("search_results.json", "w", encoding="utf-8") as file:
            json.dump(found_models, file, indent=4, ensure_ascii=False) 
        print("\nThe file has been saved.")
    elif option == 4:
        rows = load_rows()  
        if rows is None:
            return

        if not rows:
            print("\n[!] No data available to export.")
            return      
        
        with open("all_models.json", "w", encoding="utf-8") as file:
            json.dump(rows, file, indent=4, ensure_ascii=False)
        print("\nThe file has been saved.")
    elif option == 5:
        return


# 8 Выводит информацию о базе данных. / Displays information about the database. 
def show_datab_ase_info():
    rows = load_rows()
    if rows is None:
        return

    leaderboard = build_leaderboard(rows)

    total_runs = 0
    total_passed = 0
    total_attempted = 0

    models = len(rows)
    benchmarks = len(set(row["source"] for row in rows ))
    total_tasks = rows[0]["n_tasks_attempted"]

    pass_rate_average = sum(row["pass_rate"] for row in rows) / len(rows)
    average_model = min(leaderboard, key=lambda row: abs(row["pass_rate"] - pass_rate_average))
    best_model = max(leaderboard, key=lambda row: row["pass_rate"])
    lowest_model = min(leaderboard, key=lambda row: row["pass_rate"])
    average_cost = sum(row["mean_cost_usd"] for row in rows) / len(rows)
    average_duration = sum(row["mean_duration_seconds"] for row in rows) / len(rows)
    average_steps = sum(row["mean_agent_steps"] for row in rows) / len(rows)

    for row in rows:
        total_runs += row["n_runs"]
        total_passed += row["n_passed"]
        total_attempted += row["n_attempted"]  

    print(f"""  
DATABASE OVERVIEW

Models               : {models}
Benchmarks           : {benchmarks}
Total Runs           : {total_runs}
Total Tasks          : {total_tasks}
 

PERFORMANCE

Total Passed         : {total_passed}
Total Attempted      : {total_attempted}
Average Pass Rate    : {pass_rate_average * 100:.2f}% — ({average_model["model"]})
Best Pass Rate       : {best_model["pass_rate"] * 100:.2f}% — ({best_model["model"]})
Lowest Pass Rate     : {lowest_model["pass_rate"] * 100:.2f}% — ({lowest_model["model"]})


COST & PERFORMANCE

Average Cost         : {average_cost:.2f}$
Average Duration     : {average_duration:.2f}sec
Average Agent Steps  : {average_steps:.2f}
""")
