# 🚀 Distributed LMS with LLM Tutoring & Raft Consistency

A **robust, fault-tolerant Learning Management System (LMS)** designed for distributed environments.  
This project integrates a **lightweight language model (LLM)** for real-time tutoring and implements the **Raft consensus protocol** to ensure data consistency across multiple servers.

> 🧠 *Developed as part of the **Advanced Operating Systems** course — this project bridges Distributed Systems, RPC, and AI-driven educational assistance.*

---

## 🧭 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Why This Project?](#why-this-project)
- [System Architecture](#system-architecture)
- [Key Components](#key-components)
- [How It Works](#how-it-works)
- [Demo Video](#demo-video)
- [Setup Instructions](#setup-instructions)
- [Usage Guide](#usage-guide)

---

## 🏗️ Project Overview

This project implements a **Distributed Learning Management System (LMS)** where students and instructors interact through a **Python-based GUI client**.

- 📡 Multiple LMS servers operate under the **Raft consensus algorithm** for fault tolerance.  
- 🤖 A lightweight **GPT-2 model** provides real-time tutoring responses.  
- 💾 All critical data (grades, submissions, feedback) is **replicated across all nodes** for strong consistency.

**Tech Stack:** `Python` · `gRPC` · `Tkinter` · `PyTorch` · `Transformers` · `Raft Protocol`

---

## ✨ Features

- 🖥️ **Distributed Architecture** — Multiple LMS servers with Raft-based leader election and log replication  
- 🧠 **LLM Tutoring** — Real-time, context-aware GPT-2 model responses to student queries  
- 🧾 **Data Consistency** — Critical data synchronized across all nodes using Raft  
- ⚙️ **Fault Tolerance** — Seamless recovery and operation even if servers fail  
- 🎓 **Student/Instructor GUI** — Simple, interactive Tkinter client  
- 📚 **PDF Management** — Upload/download course materials and assignments  
- 🔍 **Semantic Query Validation** — BERT-based query-assignment relevance check  

---

## 💡 Why This Project?

| Goal | Description |
|------|--------------|
| **Demonstrate Distributed Systems** | Showcases leader election, log replication, and fault tolerance via Raft |
| **Integrate Modern AI** | Adds real-time tutoring with a local GPT-2 model |
| **Ensure Consistency** | Uses Raft to maintain uniform state across all servers |
| **Provide Real-World Relevance** | Simulates a production-grade distributed LMS with advanced features |




---

## 🧩 Key Components

| File | Description |
|------|--------------|
| `lms.proto` | Protocol Buffers definitions for RPCs and messages |
| `lms_server.py` | Main LMS logic + Raft consensus implementation |
| `lms_gui_final.py` | Tkinter-based GUI client for interaction |
| `tutoring_server.py` | GPT-2-based AI tutor |
| `lms_pb2.py`, `lms_pb2_grpc.py` | Auto-generated gRPC stubs |
| `Report.txt` | Full design report and analysis |

---

## ⚙️ How It Works

1. **User Login** — Students & instructors log in via the GUI client.  
2. **Assignment Handling** — Students upload PDFs; instructors download, grade, and give feedback.  
3. **Course Materials** — Instructors upload and share course materials.  
4. **Query System**  
   - Queries validated using **BERT cosine similarity** for relevance.  
   - If valid, forwarded to **GPT-2 tutoring server** for real-time assistance.  
5. **Data Consistency** — Grades, progress, and materials replicated across nodes via **Raft**.  
6. **Leader Election** — On node failure, Raft elects a new leader ensuring no data loss.

---

## 🎥 Demo Video

🎬 **[Click here to watch the full demo](https://drive.google.com/file/d/15P_hOyWWGB91ECmnMVnaSa0G2aQIvv6b/view?usp=sharing)**

The demo shows:
- Multi-node Raft setup  
- GUI-based interactions  
- LLM tutoring and fault-tolerant synchronization

---

## 🧰 Setup Instructions

### 🔑 Prerequisites
- **Python 3.9+**
- Install required packages:
  ```bash
  pip install grpcio grpcio-tools transformers protobuf PyPDF2 torch


  ⚙️ Steps

Generate gRPC Code

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. lms.proto


Configure Server IPs
Edit the IPs/ports in lms_server.py and lms_gui_final.py.

Run LMS Servers

python lms_server.py 1 50051 <peer1> <peer2> <peer3>
python lms_server.py 2 50052 <peer1> <peer2> <peer3>


Start Tutoring Server

python tutoring_server.py


Launch GUI Client

python lms_gui_final.py

🧑‍💻 Usage Guide
👩‍🎓 For Students

Upload assignments (PDF)

Ask questions (LLM or instructor)

View grades and feedback

Access course materials

👨‍🏫 For Instructors

Upload materials

Download & grade assignments

Reply to student queries

🤖 LLM Tutoring

Queries validated for topic relevance via BERT embeddings

Relevant queries are answered by GPT-2 in real time

