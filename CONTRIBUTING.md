# Contributing

## Workflow

1. Create a branch for your change.
2. Make the smallest focused edit that solves the problem.
3. Run the script or relevant checks before opening a pull request.

## Guidelines

- Keep the script's output as JSON only.
- Prefer small, readable changes over broad refactors.
- Update the README or getting-started guide when usage changes.

## Suggested Checks

```bash
python fetch_model_price.py -h
python fetch_model_price.py DLEX4000W
```