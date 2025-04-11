# gmod_luals_workflow

Runs a check on your project, using [LuaLS](https://github.com/LuaLS/lua-language-server) and [glua-api-snippets](https://github.com/luttje/glua-api-snippets).


## Usage
Create a new file in your project directory called `.github/workflows/luals.yml` and copy the following code into it:

```yaml
name: LuaLS

# You can change the triggers however you'd like
# https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows
on:
  pull_request:

jobs:
  luals:
    uses: CFC-Servers/gmod_luals_workflow/.github/workflows/luals.yml@main
```

It's that simple! Your PR will receive annotations for any issues found by LuaLS.
