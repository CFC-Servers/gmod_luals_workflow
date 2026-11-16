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

It's that simple! Your PR will receive annotations for any issues found by LuaLS. Errors fail the check, and warnings are annotated without failing it.

Code style warnings are off by default. To turn them on, pass `style_check: true`:

```yaml
jobs:
  luals:
    uses: CFC-Servers/gmod_luals_workflow/.github/workflows/luals.yml@main
    with:
      style_check: true
```

To disable a diagnostic or declare globals for your project, add a [`.luarc.json`](https://luals.github.io/wiki/configuration/) to the root of your repository. Its settings are merged with the ones this workflow provides.
