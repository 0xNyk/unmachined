# Maintainer guide

This repository keeps intelligent editing separate from publication. Agents may
inspect, edit, and verify on a topic branch. A human authorizes commits, pushes,
pull requests, merges, tags, and releases.

## GitHub repository settings

Configure a branch ruleset for `main`:

- require changes through a pull request;
- require the `self-scan` and `behavior` checks;
- require conversation resolution;
- block force pushes and branch deletion;
- require linear history if squash or rebase merges are used;
- prevent bypass when a second maintainer joins.

Do not require an independent approval while the project has one maintainer;
that would prevent ordinary releases. Add one required approval and CODEOWNER
review before granting another person merge access.

Enable secret scanning, push protection, Dependabot alerts, and private
vulnerability reporting. Keep Actions restricted to selected verified actions
and read-only `GITHUB_TOKEN` permissions unless a workflow documents why it
needs more.

These are GitHub settings, not repository files. Review them after ownership,
plan, or maintainer changes.

After branding or README image changes, upload
`assets/brand/social-card.png` under Settings → General → Social preview so
link unfurls match the repo. Brand tokens and asset inventory live in
`docs/brand.md`.

## Change flow

1. Start from an up-to-date `main` and create `agent/<short-task>` or another
   descriptive topic branch.
2. Inspect the working tree before editing. Preserve unrelated changes.
3. Make the smallest cohesive change and run the commands in `AGENTS.md`.
4. Stage explicit paths or hunks. Inspect the staged diff and rerun applicable
   checks against the staged result.
5. Commit only after authorization. Push only the current topic branch after a
   separate authorization.
6. Open a pull request using the repository template. Merge after required
   checks pass and every review thread is resolved.

## Releases

1. Move completed entries from `Unreleased` in `CHANGELOG.md` to a dated
   semantic version.
2. Set the same version in `SKILL.md` metadata.
3. Validate on every supported Python version through CI.
4. Merge the release pull request.
5. Create a signed or annotated `vX.Y.Z` tag from the merge commit and publish
   GitHub release notes from the changelog.
6. Never move an existing release tag. Publish a patch release for corrections.

The repository has no package build or runtime dependencies. Do not add a
release artifact until a host or registry requires one; the tagged source tree
is the distributable skill.

## Periodic maintenance

- Review Dependabot pull requests monthly.
- Check the GitHub community profile and security overview before each release.
- Revalidate host discovery paths and Agent Skills frontmatter for minor
  releases.
- Run an OpenSSF Scorecard review when CI, permissions, or release automation
  changes.
- Archive stale issue forms and policies instead of leaving inaccurate guidance.
