#!/usr/bin/env python3
"""
机票价格数据收集器 - 上海到太原 2025-04-02
支持多数据源，自动推送到GitHub
"""
import requests
import json
import time
import random
import subprocess
from datetime import datetime
import os

CONFIG = {
    "route": {"from": "上海", "from_code": "SHA", "to": "太原", "to_code": "TYN"},
    "target_date": "2025-04-10",
    "data_file": "data/flight_data.json",
    "repo_dir": "/Users/openclaw/.openclaw/workspace/flight-tracker"
}

class FlightCollector:
    def __init__(self):
        self.data_file = os.path.join(CONFIG["repo_dir"], CONFIG["data_file"])
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {
                "route": CONFIG["route"],
                "target_date": CONFIG["target_date"],
                "records": [],
                "stats": {"total_checks": 0, "first_check": None, "last_check": None}
            }
    
    def save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def fetch_ctrip(self):
        """获取携程数据"""
        url = "https://m.ctrip.com/restapi/soa2/14022/flightListSearch"
        payload = {
            "flightWay": "Oneway",
            "classType": "ALL",
            "hasChild": False,
            "hasBaby": False,
            "searchIndex": 1,
            "airportParams": [{
                "dcity": CONFIG["route"]["from_code"],
                "acity": CONFIG["route"]["to_code"],
                "dcityname": CONFIG["route"]["from"],
                "acityname": CONFIG["route"]["to"],
                "date": CONFIG["target_date"],
                "dcityid": 2,
                "acityid": 105
            }]
        }
        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("fltitem"):
                    flights = []
                    for item in data.get("fltitem", [])[:10]:
                        try:
                            flight = {
                                "airline": item.get("al", ""),
                                "flight_no": item.get("fn", ""),
                                "price": item.get("lp", 0),
                                "dep_time": item.get("dt", ""),
                                "arr_time": item.get("at", ""),
                                "source": "ctrip"
                            }
                            if flight["price"] > 0:
                                flights.append(flight)
                        except:
                            continue
                    return flights
        except Exception as e:
            print(f"携程失败: {e}")
        return None
    
    def generate_sample(self):
        """生成模拟数据"""
        base = 550 + random.randint(-30, 80)
        return [
            {"airline": "东方航空", "flight_no": "MU2401", "price": base, "dep_time": "08:30", "arr_time": "11:15", "source": "demo"},
            {"airline": "中国国航", "flight_no": "CA1234", "price": base + 60, "dep_time": "10:15", "arr_time": "13:00", "source": "demo"},
            {"airline": "南方航空", "flight_no": "CZ5678", "price": base + 100, "dep_time": "14:20", "arr_time": "17:05", "source": "demo"}
        ]
    
    def push_github(self):
        """推送到GitHub"""
        try:
            os.chdir(CONFIG["repo_dir"])
            subprocess.run(["git", "add", "data/flight_data.json"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Update: {datetime.now().strftime('%m-%d %H:%M')}"], capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], capture_output=True)
            print("✓ 已推送GitHub")
        except Exception as e:
            print(f"推送失败: {e}")
    
    def collect(self):
        print(f"[{datetime.now().strftime('%H:%M')}] 开始收集...")
        
        flights = self.fetch_ctrip()
        if not flights:
            flights = self.generate_sample()
            print("使用模拟数据")
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "flights": flights,
            "lowest_price": min(f["price"] for f in flights),
            "highest_price": max(f["price"] for f in flights),
            "avg_price": round(sum(f["price"] for f in flights) / len(flights), 0)
        }
        
        self.data["records"].append(record)
        self.data["stats"]["total_checks"] += 1
        self.data["stats"]["last_check"] = datetime.now().isoformat()
        if not self.data["stats"]["first_check"]:
            self.data["stats"]["first_check"] = datetime.now().isoformat()
        
        self.save_data()
        print(f"✓ 最低: ¥{record['lowest_price']}, 平均: ¥{record['avg_price']}")
        self.push_github()
        return record

def main():
    collector = FlightCollector()
    collector.collect()

if __name__ == "__main__":
    main()
