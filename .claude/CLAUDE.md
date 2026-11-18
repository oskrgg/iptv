# Notes for Claude

This is oskrgg's fork of iptv-org/iptv (`origin` = oskrgg/iptv, `upstream` = iptv-org/iptv).

## Git

- **Never run `git commit` or `git push`.** Make the file changes, then tell the user what changed. The user commits and pushes themselves.

## TV playlist: `streams/my-cr.m3u`

- The user's TV loads https://oskrgg.github.io/iptv/streams/my-cr.m3u, which GitHub Pages serves from `master` of this fork. Changes reach the TV only after the user commits and pushes.
- "my-cr" means `streams/my-cr.m3u`, a hand-picked list of Costa Rica channels plus Popcorn Central. It is a different file from `streams/oskrgg.m3u`.
- To update, refresh, check or change it, use the `update-my-cr` skill in `.claude/skills/update-my-cr/`. It holds the steps, the scripts and the channel rules.
