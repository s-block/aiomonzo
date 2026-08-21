# Codex cloud environment

Create the Codex cloud environment for `s-block/aiomonzo` with the default
`universal` image and these settings:

- Python: `3.12`
- Setup script: `bash .codex/setup.sh`
- Maintenance script: `bash .codex/setup.sh`
- Environment variables and secrets: none required for validation

The script installs the locked development environment and prepares the
pre-commit hook environments while setup-phase internet access is available.
Normal agent work can keep internet access disabled.

See the [Codex cloud environment documentation](https://developers.openai.com/codex/cloud/environments)
for the environment lifecycle and cache behavior.
