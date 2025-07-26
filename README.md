# Roy'sCode - A Tech-Themed Online Code Judge

[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-darkgreen.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-24-blue.svg?logo=docker)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-Deployed-orange.svg?logo=amazon-aws)](https://aws.amazon.com/)

Roy'sCode is a full-stack web application that provides a complete competitive programming platform, wrapped in an immersive and engaging Dark Tech theme. It's designed to be a comprehensive and interactive learning tool, backed by a professional, scalable, and secure cloud architecture.

---

### **[Website Link](http://43.204.98.112:8000/)**

**Note:** The application is hosted on an AWS Free Tier EC2 instance and is not configured with a custom domain or SSL.

### Screenshot

![DEMO Video](https://drive.google.com/drive/folders/1wSndazeoIzb_UPJDNI1fZTUCWGoY-n-S)
---

## Features & Functionality

Roy'sCode is packed with features designed to create a complete and engaging user experience from login to leaderboard.

### Core User Journey & Dashboard

*   **Personalized Experience:** Users can sign up, log in, and manage a personal profile that tracks their progress and preferences.
*   **Interactive Dashboard:** The main hub for all challenges, featuring:
    -   **Topic Organization:** Problems are neatly sorted into categories like Arrays, Strings, Linked Lists, Trees, Graphs, and DP.
    -   **Difficulty Tags:** Each problem is clearly marked as Easy, Medium, or Hard.
    -   **Powerful Search:** A search bar allows users to quickly find specific problems.
*   **Automated Progress Tracking:** A key motivating feature. When a user successfully solves a problem, it gets an automatic **checkmark (✔)** on the dashboard, providing a clear visual of their accomplishments.

### The Coding Arena & Tools

*   **Integrated Solving Environment:** A clean, two-panel layout with the problem description on the left and a sleek, multi-language code editor on the right.
*   **Instant Feedback Loop:**
    -   **Run Code:** Test solutions against public sample cases for quick, iterative development.
    -   **Submit:** Send the final solution for judgment against a comprehensive suite of hidden test cases.
*   **⭐ AI-Powered Assistance:** A unique "AI Help" button is available within the problem-solving page, offering intelligent style analysis and code overview and improvements along with the Debugging analysis with the corrected code if the code is buggy.

### Community & Utility Features

*   **Live Leaderboard:** A competitive leaderboard to see how users rank against each other, fostering an engaging community.
*   **Personalized Favorites List (★):** Users can star any problem to add it to a personal favorites list for easy review and practice.
*   **Comprehensive Submission History:** A dedicated "Submissions" page where users can review the verdicts, code, and timestamps of all their past attempts.
*   **Standalone Compiler:** A separate compiler page allows users to write and run code snippets freely, outside the context of a specific problem.

---

## Tech Stack & Architecture

Roy'sCode is built on a modern, scalable technology stack, designed for performance, security, and maintainability.

-   **Backend:** Django, Gunicorn
-   **Database:** PostgreSQL
-   **Frontend:** Django Templates, HTML, Tailwind CSS
-   **DevOps & Containerization:** Docker, Docker Compose

### Cloud Architecture on AWS

The application is fully deployed on Amazon Web Services, using a separated architecture for robustness and security.

-   **EC2 (Elastic Compute Cloud):** A virtual Linux server that acts as the secure host for our running Docker container.
-   **RDS (Relational Database Service):** A managed PostgreSQL database that lives independently from the application server. This ensures that all user and problem data is persistent, secure, and safely backed up.
-   **ECR (Elastic Container Registry):** A private Docker registry used to store and version our application images. This enables consistent and reliable deployments.
-   **IAM & Security Groups:** A combination of a dedicated IAM user and a strict virtual firewall ensures that the application and server are only accessible through defined, secure channels.

---

