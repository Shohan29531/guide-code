# GuidedCode

A Streamlit coding-practice platform that teaches problem-solving through guided reasoning, progressive hints, local test execution, mistake diagnosis, and mastery tracking.

## Setup with Conda

From the extracted project folder:

```bash
conda env create -f environment.yml
conda activate guided-code-lab
streamlit run app.py
```

Or create the environment directly:

```bash
conda create -n guided-code-lab -c conda-forge python=3.11 "streamlit>=1.60,<2" "pandas>=2.2,<3" "requests>=2.32,<3" -y
conda activate guided-code-lab
streamlit run app.py
```

## Included

- 500 coding problems with starter code for Python, C, C++, C#, Java, JavaScript, and Go
- Local built-in test execution for Python and JavaScript
- LeetCode-style Testcase/Test Result console with Run and Submit actions
- Independent saved drafts for every problem and language
- Detailed problem descriptions and explained examples
- Compact visual models for geometry, grids, intervals, graphs, and transformations
- Active-recall prediction checks before worked answers
- Structured reasoning checkpoints before coding
- Arrays, strings, hashing, stacks, queues, matrices, graphs, binary search, dynamic programming, greedy algorithms, and backtracking
- Guided decomposition questions
- Four-level progressive hints
- 1,278 built-in judge cases
- Automatic mistake classification for progress tracking
- Independent, guided, and assisted solve tracking
- Three-day recall queue for spaced practice
- SQLite drafts, attempts, and concept-mastery tracking
- Personalized next-problem recommendations
- White light-mode interface
- JSON progress export

## Deployment note

The bundled Python and JavaScript runners are intended for local prototyping.
Before public deployment—or before enabling compiled-language execution—run
learner code in isolated containers or use a dedicated judge service such as
Judge0.
# guide-code
