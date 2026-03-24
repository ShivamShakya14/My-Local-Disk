# 🚀 My Local Disk

**My Local Disk** is a self-hosted file manager built using Flask that allows you to upload, manage, and access files from your PC through a web browser over a local network.

It works like a lightweight personal cloud storage system (similar to Google Drive or Dropbox), but everything runs locally on your machine.

---

## ✨ Features

- 📁 Browse files and folders
- ⬆️ Upload single or multiple files (Drag & Drop supported)
- ⬇️ Download files and folders
- 📦 Batch download as ZIP
- 🗑️ Delete files and folders
- ✏️ Rename files and folders
- 📂 Create new folders
- 🔐 Simple login system
- 🌙 Dark mode support

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **UI Framework:** Bootstrap 5

---

## 📂 Project Structure
```
my-local-disk/
│── app.py
│── shared/ # File storage directory
│── templates/
│ ├── index.html
│ └── login.html
│── static/
│ ├── script.js
│ └── style.css
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/shivamshakya14/my-local-disk.git
cd my-local-disk
```

### 2️⃣ Install Dependencies
```base
pip install flask
```
### 3️⃣ Run the Application
```base
python app.py
```

### 4️⃣ Open in Browser
```base
http://localhost:8214
```

🔐 Default Login Credentials
```
Username: admin
Password: admin
```
⚠️ You can change these in app.py

📦 How It Works
🔹 File Storage

All uploaded files are stored in the shared/ folder inside the project directory.

🔹 File Access

The application provides a browser-based interface where you can:

Navigate folders
Upload files
Download files
Manage files (rename/delete)

🔹 Local Network Access

You can access the app from other devices on the same WiFi.

Find your PC's local IP address (e.g. 192.168.1.5)
Open in another device:
```
http://192.168.1.5:8214
```

🔹 Upload System
Drag & drop files into the upload area
Or click to select files
Files are saved in the current folder

📸 Screenshots
<img width="2857" height="1257" alt="image" src="https://github.com/user-attachments/assets/6ea00e0c-aaf3-4a69-bf7a-6e283cb0cfbf" />

<img width="2861" height="843" alt="image" src="https://github.com/user-attachments/assets/a6152360-d7e1-48b5-a921-d6fd785f0486" />

📜 License

This project is open-source and free to use.

🙌 Author

Created by Shivam Shakya

