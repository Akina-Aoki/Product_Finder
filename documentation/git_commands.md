# Git commands to create your own branch

## Step 1 — Make Sure You’re on main
```
git checkout main
```

Expected. 
```
Already on 'main'
Your branch is up to date with 'origin/main'.
```

If your main is aligned with main, proceed:
```
git pull origin main
```

Expected:
```
 * branch            main       -> FETCH_HEAD
Already up to date.
```
This guarantees your branch starts from the latest remote state.

## Step 2 — Create a New Feature Branch
Use a naming convention that reflects feature. Sample:
```
git checkout -b feat/(name_of your_feature/task)
```

Expected:
```
Switched to a new branch <branch_name>
```


## Step 3 — Push the Branch and Track It
ONLY PUSH TO YOUR BRANCH UNTIL Scrum Master and Product Owner approves.
```
git push -u origin <branch_name>
```

## Step 4 - Confirm
```
git branch
```
Your active branch should show with *.

---

## If you want to keep on working in the same branch and want to push to your branch in github
Check your branch
```
git branch
```

Should work in your own branch:
```
* <branch_name>
main
```

NEVER PUSH ON MAIN
```
git add .
git commit -m "feat: implement X"
git push
```
.