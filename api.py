
from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)
DATA_FILE = 'data/leaderboard.json'

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/submit', methods=['POST'])
def submit_result():
    payload = request.json
    mc_name = payload.get('mc_name')
    discord_name = payload.get('discord_name')
    mode = payload.get('mode')
    tier = payload.get('tier')

    if not all([mc_name, discord_name, mode, tier]):
        return jsonify({'error': 'Thiếu dữ liệu'}), 400

    data = load_data()
    if mode not in data:
        data[mode] = []

    existing = next((p for p in data[mode] if p["mcName"] == mc_name), None)
    if existing:
        existing["tier"] = tier
        existing["score"] = tier_to_score(tier)
        existing["testCount"] += 1
    else:
        data[mode].append({
            "rank": 9999,
            "mcName": mc_name,
            "tier": tier,
            "score": tier_to_score(tier),
            "testCount": 1
        })

    data["overall"] = calculate_overall(data)
    save_data(data)
    return jsonify({'message': 'Đã nhận tier thành công!'})

@app.route('/delete', methods=['DELETE'])
def delete_tier():
    payload = request.json
    mc_name = payload.get("mc_name")
    mode = payload.get("mode")
    data = load_data()
    if mode not in data:
        return jsonify({"error": "Mode không tồn tại"}), 400
    data[mode] = [p for p in data[mode] if p["mcName"] != mc_name]
    data["overall"] = calculate_overall(data)
    save_data(data)
    return jsonify({"message": "Đã xoá thành công"})

@app.route('/profile/<mc_name>', methods=['GET'])
def profile(mc_name):
    data = load_data()
    profile = {"mcName": mc_name}
    for mode in data:
        if mode == "overall":
            continue
        player = next((p for p in data[mode] if p["mcName"] == mc_name), None)
        if player:
            profile[mode] = player["tier"]
            profile[f"{mode}_score"] = player["score"]
    overall = next((p for p in data["overall"] if p["mcName"] == mc_name), None)
    if overall:
        profile.update({
            "overallScore": overall["overallScore"],
            "overallTier": overall["overallTier"],
            "rank": overall["rank"]
        })
    return jsonify(profile)

def tier_to_score(tier):
    tier_map = {
        "HT1": 100, "HT2": 95, "HT3": 90, "HT4": 85, "HT5": 80,
        "LT1": 75, "LT2": 70, "LT3": 65, "LT4": 60, "LT5": 55
    }
    return tier_map.get(tier.upper(), 50)

def calculate_overall(data):
    overall = {}
    for mode, players in data.items():
        if mode == "overall":
            continue
        for p in players:
            name = p["mcName"]
            score = p["score"]
            if name not in overall:
                overall[name] = {
                    "mcName": name,
                    "modes": {},
                    "scores": [],
                    "testCount": 0
                }
            overall[name]["modes"][mode] = {"tier": p["tier"], "score": score}
            overall[name]["scores"].append(score)
            overall[name]["testCount"] += p.get("testCount", 1)

    overall_list = []
    for name, info in overall.items():
        avg_score = round(sum(info["scores"]) / len(info["scores"]), 2)
        entry = {
            "mcName": name,
            "overallScore": avg_score,
            "testCount": info["testCount"]
        }
        for mode, val in info["modes"].items():
            entry[mode] = val["tier"]
        entry["overallTier"] = score_to_tier(avg_score)
        overall_list.append(entry)

    overall_list.sort(key=lambda x: x["overallScore"], reverse=True)
    for idx, p in enumerate(overall_list):
        p["rank"] = idx + 1
    return overall_list

def score_to_tier(score):
    if score >= 97: return "HT1"
    elif score >= 93: return "HT2"
    elif score >= 88: return "HT3"
    elif score >= 83: return "HT4"
    elif score >= 78: return "HT5"
    elif score >= 73: return "LT1"
    elif score >= 68: return "LT2"
    elif score >= 63: return "LT3"
    elif score >= 58: return "LT4"
    else: return "LT5"

if __name__ == '__main__':
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"overall": []}, f)
    app.run(port=5000)
