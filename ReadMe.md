
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
