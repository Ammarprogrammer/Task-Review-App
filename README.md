# 📝 Task Manager & Progress Tracking App

A Python-based console application that helps users manage daily tasks, track work progress, and measure completion percentages. The system uses OOP principles and stores all user accounts and tasks in a single JSON file.

---

## 🚀 Features

### 👤 Account Management
- Create a new account (8-character alphanumeric password required)
- Auto-generated unique user ID
- Secure login system
- Delete account (password confirmation required)

### 📌 Task Management
- Add tasks with assigned duration
- Update tasks with actual duration worked
- Automatic calculation of **completion percentage**
- Tasks stored in this format:

```json
{
  "task_name": "Study SQL",
  "assigned_duration": 2,
  "actual_duration": 1.5,
  "date": "2025-11-13",
  "completion_percent": 75.0
}
