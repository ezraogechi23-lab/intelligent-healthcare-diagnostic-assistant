# Contributing to This Project

Team workflow for the Intelligent Healthcare Diagnostic Assistant capstone.

## One-time setup (everyone does this once)

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Every work session

**1. Before you start working, sync with the latest changes:**
```bash
git checkout main
git pull origin main
```

**2. Create a branch for what you're working on:**
```bash
git checkout -b feature/<yourname>-<what-you're-doing>
# examples:
# git checkout -b feature/ezra-fix-nlp-module
# git checkout -b feature/sarah-add-symptom-validation
```

**3. Make your changes, then commit them:**
```bash
git add .
git commit -m "Clear description of what changed and why"
```

**4. Push your branch to GitHub:**
```bash
git push origin feature/<yourname>-<what-you're-doing>
```

**5. Open a Pull Request on GitHub:**
- Go to the repo on GitHub — you'll see a banner "Compare & pull request." Click it.
- Give it a clear title and describe what you changed and why.
- Request a review from at least one teammate.
- Do **not** merge your own PR without a review, even if you're confident it's correct.

**6. After your PR is approved and merged**, delete the branch (GitHub offers a
button for this) and go back to step 1 for your next task.

## Rules

- Never push directly to `main`. All changes go through a Pull Request.
- One module/feature per branch — don't mix unrelated changes in one PR.
- Pull `main` before starting new work, to avoid painful merge conflicts later.
- If you touch a file someone else is actively working on, say so in the team
  chat before you start.
- Use [GitHub Issues](../../issues) to claim a task before starting it, so two
  people don't accidentally duplicate work.

## Who owns what (fill this in as a team)

| Module | Owner |
|---|---|
| `modules/agent.py` | |
| `modules/knowledge_base.py` | |
| `modules/bayesian_net.py` | |
| `modules/ml_classifier.py` | |
| `modules/neural_network.py` | |
| `modules/fuzzy_controller.py` | |
| `modules/planner.py` | |
| `evaluation/` | |
| `app.py` / integration | |
| Final report / demo | |
