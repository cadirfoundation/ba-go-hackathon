# BA_Go: Agentic Cinema Decision Control Room 🎬

BA_Go is an AI-powered executive decision dashboard designed for MicroDrama streaming platforms (AVOD & SVOD). Built for the **Agentic Cinema Hackathon**, it leverages Gemini 2.5 Pro and ClickHouse Cloud to process real-time telemetry, analyze regional drop-off rates, and generate data-driven operational actions to maximize AdMob revenue and viewer retention.

## 🚀 Hackathon Tracks Integrated
* **Google Cloud & Gemini:** Uses `google-genai` and Gemini 2.5 Pro to power the core Hypothesis Engine, generating dynamic ClickHouse SQL queries based on natural language prompts.
* **ClickHouse:** Acts as the central OLAP warehouse, ingesting simulated real-time data streams (telemetry, AdMob APIs, Google Ads CPI) and serving lightning-fast aggregations to the Streamlit frontend.

## 🛠 Prerequisites
* Python 3.11+
* A ClickHouse Cloud instance
* A Google Cloud Project with the Vertex AI API enabled

## ⚙️ Local Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/cadirfoundation/ba-go-hackathon.git
cd ba-go-hackathon