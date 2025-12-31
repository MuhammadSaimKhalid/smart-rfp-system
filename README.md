# Smart RFP System v2.2

<div align="center">
  <img src="docs/images/logo-placeholder.png" alt="Smart RFP Logo" width="120" />
  <h1>Smart RFP System</h1>
  <p><strong>AI-Powered Procurement & Proposal Management</strong></p>

  <p>
    <a href="#key-features">Features</a> •
    <a href="#how-it-works">How It Works</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="WORKFLOW.md">Documentation</a>
  </p>

  <br />

  <img src="docs/images/dashboard-hero.png" alt="Smart RFP Dashboard" width="800" />
</div>

---

## 💡 About The Project

**Smart RFP** is an intelligent web application designed to revolutionize the way organizations handle Request for Proposals (RFPs). By leveraging advanced AI, it automates the tedious extraction of data from vendor proposals, enables dynamic apple-to-apple comparisons, and provides data-driven insights to help procurement teams make the best decisions faster.

Traditional procurement is slow and manual. Smart RFP makes it **instant**, **analytical**, and **visual**.

---

## ✨ Key Features

### 📄 AI Proposal Extraction
Stop manually reading hundreds of pages. Drag and drop PDF proposals, and our AI engine instantly extracts:
-   **Vendor Details & Pricing**: Automatically captures total costs.
-   **Executive Summaries**: Generates concise summaries of lengthy documents.
-   **Credential Analysis**: Highlights relevant vendor experience.

### 📊 Intelligent Comparison Engine
Compare vendors side-by-side with precision.
-   **Dynamic Dimensions**: The system extracts requirements from *your* RFP (e.g., "24/7 Support", "ISO Compliance") and scores every vendor against them.
-   **Weighted Scoring**: Vendors are graded (0-100) on each dimension.
-   **Visual Reports**: Radar charts and bar graphs make decision-making obvious.

### ⚡ Real-Time Dashboard
-   Track **Open RFPs**, **Active Proposals**, and **Drafts** in one view.
-   Monitor the status of every ongoing procurement project.

### 🔐 Secure & Modern
-   Role-based workflows.
-   Secure document storage.
-   Clean, responsive UI built with React & TailwindCSS.

---

## 🛠 Tech Stack

### Frontend
-   **React 19**: Modern UI library for a seamless user experience.
-   **Vite**: Blazing fast build tool.
-   **TailwindCSS**: Utility-first CSS for beautiful, custom designs.
-   **ApexCharts**: Interactive data visualization for comparison reports.

### Backend
-   **Python 3.10+**: Core logic and AI orchestrator.
-   **FastAPI**: High-performance web framework for APIs.
-   **SQLite/PostgreSQL**: Robust data persistence.
-   **AI Services**: Integrated LLMs for document parsing and scoring.

---

## 🚀 Getting Started

Follow these steps to set up the project locally. For a detailed walkthrough, see [WORKFLOW.md](WORKFLOW.md).

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)

### Installation

#### 1. Backend Setup
```bash
# Clone the repo
git clone https://github.com/saim-honey388/smart-rfp-system.git
cd smart-rfp-system

# Install Python dependencies
pip install -r requirements.txt

# Start the API server
python -m apps.api.main
```

#### 2. Client Setup
```bash
# Open a new terminal
cd apps/client

# Install Node dependencies
npm install

# Start the frontend
npm run dev
```

Visit `http://localhost:5173` to view the app!

---

## 📸 Snapshots

| Create RFP | Proposal Analysis |
|:---:|:---:|
| <img src="docs/images/create-rfp.png" alt="Create RFP" width="400"/> | <img src="docs/images/proposal-analysis.png" alt="Proposal Analysis" width="400"/> |

| Comparison Report | Radar Chart |
|:---:|:---:|
| <img src="docs/images/comparison.png" alt="Comparison" width="400"/> | <img src="docs/images/radar-chart.png" alt="Radar Chart" width="400"/> |

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📧 Contact

**Saim Khalid** - saim.khalid983@gmail.com
Project Link: [https://github.com/saim-honey388/smart-rfp-system](https://github.com/saim-honey388/smart-rfp-system)
