import json

data = {
    "project": "backend roadmap",
    "phase": 0,
    "skills": ["python", "venv", "json"],
    "completed": True
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

try:
    with open("data.json", "r", encoding="utf-8") as f:
        loaded_data = json.load(f)


    print("Project:", loaded_data["project"])
    print("Skills:", loaded_data["skills"])

except FileNotFoundError:
    print("data.json file not found")

except json.JSONDecodeError:
    print("Invalid JSON format")