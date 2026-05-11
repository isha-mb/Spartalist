## 🏛️ Spartalist: Student Council Voting System

**Spartalist** is a Python-based election management system designed for **Batangas State University** student organizations. It provides a secure, automated way to handle candidate storage, voter registration, and real-time result tallying using fundamental data structures.

### ✨ Key Features

* **Strict ID Validation:** Enforces the university’s `##-#####` student number format using Regular Expressions (Regex) to ensure only valid students can register.
* **Anti-Fraud Mechanism:** Utilizes a Hash Map (Dictionary) to track voter participation, instantly preventing duplicate votes for the same position.
* **Dynamic Balloting:** Automatically generates ballots based on customizable party-list configurations and executive positions.
* **Password-Protected Admin Panel:** A secure area for election officers to monitor live leaderboards, view the registered voter list, and finalize results.
* **Automated Reporting:** Generates a professional `.txt` election report including total voter turnout, vote distribution per candidate, and the declared winners.

### 💻 Technical "Stuffs" (Data Structures)

The system is built as a practical application of Computer Science fundamentals:

* **Singly Linked Lists:** Used for candidate management. Each position (President, VP, etc.) is a separate list where nodes store candidate metadata and vote tallies, allowing for efficient sequential processing.
* **Hash Maps & Sets:** Used for $O(1)$ voter lookups. By mapping Student IDs to a set of voted-for positions, the system ensures high-speed verification even as the voter database grows.
* **File I/O & Regex:** Handles persistent data export and string pattern matching for robust input validation.
