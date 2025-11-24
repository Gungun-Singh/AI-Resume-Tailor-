# 🧠 AI Resume Tailor

AI Resume Tailor is a web application that helps job seekers align their resumes with any Job Description using intelligent skill matching and AI-powered content enhancement. Users can upload a resume PDF, paste a JD, and instantly receive tailored insights to improve their chances of getting shortlisted.

---

## 🔍 Key Features
- **Matched vs Missing Skills Analysis**  
- **Resume Match Score (%)**
- **Improved & Action-Driven Resume Bullet Points**
- **Tailored Cover Letter Generation**
- **Exportable Results for Job Applications**
- **Clean and Responsive UI**

---

## 🚀 Tech Stack
| Layer | Technology |
|-------|------------|
| Frontend | Streamlit (for UI) |
| Styling | CSS |
| AI Processing | Groq + CAMEL-AI Agents |
| File Handling | PDF text extraction |

---

## 📁 How It Works
1. Upload your **resume (PDF)**
2. Paste the **Job Description**
3. Application extracts context and skills
4. AI evaluates alignment and generates results:
   - Skills mapping
   - Match percentage
   - Improved resume bullets
   - Tailored cover letter
5. Export or refine outputs

---

## 🧩 Project Structure

/Resume Tailor AI
├─ app.py/
├─ agent.py/
├─ api.env/
├─ requirements.txt/



---

## ⚙️ Installation & Setup

```VS CODE TERMINAL
Create a virtual environment - python -m venv venv
Then activate venv - venv/scripts/activate
Then install the requirements - pip install -r requirements.txt
Run app - streamlit run app.py

🔑 Environment Variables

Create an api.env or .env file and include:
GROQ_API_KEY=your_key_here


🤝 Contributions

Contributions, feature requests, and suggestions are welcome.
Feel free to fork the repo and submit a PR.


