# Contributing to CleverShop Backend Core

## 🚨 Rules You Must Follow for This Repository

These rules are enforced by branch protection rules and GitHub Actions workflows. Violations can block your pull request from being merged.

---

## 🔒 Branch Protection Rules

| Branch             | Protection                                                                       |
| ------------------ | -------------------------------------------------------------------------------- |
| `main`             | Pull request required, at least 1 approval, all required status checks must pass |
| `qa`               | Pull request required, at least 1 approval, all required status checks must pass |
| `dev`              | Pull request required, at least 1 approval, all required status checks must pass |
| Protected branches | Direct pushes are not allowed                                                    |
| Protected branches | Force pushes are not allowed                                                     |
| Protected branches | Branch deletion is not allowed                                                   |

All changes to `dev`, `qa`, and `main` must go through pull requests.

---

## 📋 Pull Request Requirements

Before a pull request can be merged:

* The pull request must have at least 1 approval.
* All required GitHub Actions checks must pass.
* The branch must be up to date with the target branch.
* All conversations must be resolved.
* The pull request must follow the required branch flow.

---

## 🌿 Branch Strategy

This repository follows this update flow:

```text
feature branch -> dev -> qa -> main
```

### Branch Purposes

| Branch           | Purpose                                                   |
| ---------------- | --------------------------------------------------------- |
| `dev`            | Development integration branch for completed feature work |
| `qa`             | Testing branch used for QA validation before production   |
| `main`           | Production branch                                         |
| Feature branches | Temporary branches used for new work                      |

---

## ✅ Correct Branch Flow

### 1. Feature Work

All feature or task branches must be created from `dev`.

```bash
git checkout dev
git pull origin dev
git checkout -b your-branch-name
```

Example:

```bash
git checkout dev
git pull origin dev
git checkout -b backend-core-ci-cd
```

Feature branches should merge into `dev` through a pull request.

```text
your-branch-name -> dev
```

---

### 2. Promote Development to QA

After changes are merged into `dev` and are ready for testing, open a pull request from `dev` into `qa`.

```text
dev -> qa
```

Pull requests into `qa` should only come from `dev`.

The QA pull request workflow will run only when the pull request targets the `qa` branch.

---

### 3. Promote QA to Production

After QA testing is complete, open a pull request from `qa` into `main`.

```text
qa -> main
```

Pull requests into `main` should only come from `qa`.

---

## ❌ Incorrect Branch Flow

Do not use these flows:

```text
feature branch -> main
feature branch -> qa
dev -> main
main -> dev
main -> qa
qa -> dev
```

These flows bypass the required development, QA, and production process.

---

## ⚙️ GitHub Actions Workflows

This repository uses GitHub Actions to help enforce the branch process.

### Branch Flow Check

The branch flow check validates that pull requests follow the correct direction:

```text
feature branch -> dev
dev -> qa
qa -> main
```

If a pull request targets the wrong branch, the workflow will fail.

### QA Pull Request Checks

The QA workflow runs only on pull requests targeting the `qa` branch.

This workflow is used to validate code before it is promoted from `dev` to `qa`.

---

## 🚀 Deployment Environments

When deployment environments are configured, the expected deployment flow is:

| Branch | Environment             |
| ------ | ----------------------- |
| `dev`  | Development environment |
| `qa`   | QA/testing environment  |
| `main` | Production environment  |

Deployment environments may require manual approval before workflows complete.

---

## 🧪 Required Checks

Pull requests must pass the required checks before merging.

Required checks may include:

* Backend build
* Unit tests
* Integration tests
* Linting or formatting checks
* Docker build validation

The exact checks may change as the backend project grows.

---

## 🧑‍💻 Standard Contribution Steps

Use this process when contributing:

```bash
git checkout dev
git pull origin dev
git checkout -b your-branch-name
```

Make your changes, then commit and push:

```bash
git add .
git commit -m "Describe your change"
git push -u origin your-branch-name
```

Then open a pull request:

```text
your-branch-name -> dev
```

After the pull request is approved and all checks pass, it can be merged into `dev`.

---

## 📝 Summary

The required repository flow is:

```text
feature branch -> dev -> qa -> main
```

Do not skip branches in the process. All changes must go through pull requests, approvals, and passing status checks before reaching production.
