## How to connect to github

### 1. Configure Git with your GitHub identity

In terminal:

git config --global user.name "Your GitHub Username"
git config --global user.email "your_email@example.com"

### 2. Connect your PC to GitHub (best method: SSH)

This avoids logging in every time.

Step 4.1 — Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

Press Enter for everything.
Then copy the key in github

### 3 — Test connection
ssh -T git@github.com

You should see:

Hi username! You've successfully authenticated.

##  How to create repository
