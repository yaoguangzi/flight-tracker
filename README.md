# ✈️ 机票价格追踪器

追踪上海 → 太原（2025-04-02）的机票价格趋势。

## 🌐 在线看板

**访问地址**: `https://openclaw-bot.github.io/flight-tracker/`

## 📊 功能

- 每2小时自动抓取机票价格
- 实时价格趋势图表
- 智能购买建议
- 历史最低价追踪

## 🗂️ 文件结构

```
flight-tracker/
├── index.html          # 可视化看板
├── collector.py        # 数据收集脚本
├── data/
│   └── flight_data.json # 价格数据
└── README.md
```

## 🚀 部署

本仓库使用 GitHub Pages 托管，自动从 `data/flight_data.json` 读取数据。

## 📈 数据来源

- 携程移动端 API
- 每2小时更新一次
