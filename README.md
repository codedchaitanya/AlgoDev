# Roy'sCode - A Tech-Themed Online Code Judge

Roy'sCode is a full-stack web application that provides a complete competitive programming platform, wrapped in an immersive and engaging dark horror theme. The goal was to build not just a functional code judge, but a memorable user experience backed by a professional, scalable, and secure cloud infrastructure.

---

### **[Website Link]:- "http://43.204.98.112:8000/"**

**Note:** The application is hosted on an AWS Free Tier EC2 instance and is not configured with a custom domain or SSL.

### Screenshot

![Roy'sCode Screenshot](<img width="1905" height="918" alt="image" src="https://github.com/user-attachments/assets/ce5812ac-a1f5-4d9e-8a4c-571535e9c431" />
)

---

## Features & Functionality

Roy’sCode: A Full User-Facing Walkthrough
Welcome to Roy’sCode, an immersive, horror-themed online code judge designed for the modern coder.

1. Home & Login
When users arrive, they’re met with Roy’sCode’s eerie, engaging interface. Registration and login are seamless. Every user gets a personalized profile, showing their stats, favorites list, and submission history.

2. Dashboard: Challenge Navigation
On the main dashboard, users see:

-Topic organization: Problems sorted into categories like Arrays, Strings, Linked List, Stack & Queue, Tree, BST, Graph, and DP.

-Difficulty tags: Each problem shows if it’s Easy, Medium, or Hard.

-Favorites quick access: Users can click a ★ to add problems to their favorites list.

-Search: A search bar finds problems by name or keyword.

-Leaderboard: See how you stack up against other coders in real time.

-Auto checkmarks: When a user completely solves (accepts) a problem, it automatically gets a tick-mark, showing clear progress.

-Compiler: Accessible at any time for testing ideas—write and run code freely outside the problems!

-Profile & Logout: Profile management, account info, and instant logout are always accessible.

3. Solving a Problem: The Coding Arena
When a challenge is selected, the problem-solving page appears:

-Left side: Problem description, sample inputs, outputs, and tips.

-Right side: Code editor (supports languages like C++, Python).

-Run Code button: Instantly tests user code on sample cases.

-Submit button: Submits solution for full evaluation.

-AI Help button: Unique feature! Click “AI Help” to get context-aware hints or starter logic—perfect for breaking through frustration!

4. Submission Page
-Every code submission is tracked:

-View verdicts (Accepted, Wrong Answer, Time Limit Exceeded, etc.) for each past submission.

-Resubmit, review, or learn from your history.

5. Profile & Leaderboard
-Profile: See your solved count, favorite problems, and personal activity.

-Leaderboard: Compete with the community—see where you stand and climb the ranks.

6. Admin Portal
-Site administrators use a secure /admin backend to:

-Add/edit problems, solutions, test cases

-Review user submissions

-Manage accounts and site content

-Roy’sCode lets you solve, experiment, climb the leaderboard, and seek AI-powered help—all in a dark, electrifying environment.

-Key user-visible features:

-Dashboard with checkmarks on completion

-Favorites and search

-Live leaderboard and profile

-Submission and compiler pages

-In-problem AI Help and instant feedback

Everything updates in real time—no redeployment needed for test case uploads, admin edits, or new problems. This is your coding playground and competitive arena—all in one unique theme.

---

## Tech Stack & Architecture

Roy'sCode is built on a modern, scalable technology stack, designed for performance, security, and maintainability.

-   **Backend:** Django, Gunicorn
-   **Database:** PostgreSQL
-   **Frontend:** Django Templates, HTML, CSS, JavaScript
-   **DevOps & Containerization:** Docker, Docker Compose

### Cloud Architecture on AWS

The application is fully deployed on Amazon Web Services, using a separated architecture for robustness and security.

-   **EC2 (Elastic Compute Cloud):** A virtual Linux server that acts as the secure host for our running Docker container.
-   **RDS (Relational Database Service):** A managed PostgreSQL database that lives independently from the application server. This separation ensures that all user and problem data is persistent, secure, and safely backed up.
-   **ECR (Elastic Container Registry):** A private Docker registry used to store and version our application images. This enables consistent and reliable deployments.
-   **IAM & Security Groups:** A combination of a dedicated IAM user and a strict virtual firewall ensures that the application and server are only accessible through defined, secure channels.

---
