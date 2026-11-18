---
name: update-my-cr
description: Refresh the user's TV playlist streams/my-cr.m3u with the latest working Costa Rica stream links from iptv-org. Use when the user asks to update, refresh, check or fix "my-cr", their CR playlist, or their TV channels, or to add or remove channels in it.
---

# Update my-cr playlist

The user's TV loads https://oskrgg.github.io/iptv/streams/my-cr.m3u. GitHub Pages serves that file from `master` of the oskrgg/iptv fork, so the TV sees changes only after they are pushed.

`streams/my-cr.m3u` is a hand-picked list: Costa Rica channels plus Popcorn Central (a movie channel). It is a different file from `streams/oskrgg.m3u`.

## Rules

- **Never commit or push.** Edit the files, then tell the user what changed. The user commits and pushes themselves.
- Keep the channel list the user chose. Add or remove channels only when asked, except for the WANTED channels below.
- Keep `~/Downloads/my-cr.m3u` identical to `streams/my-cr.m3u`.
- Channel names show only the resolution, for example `Canal 4 (720p)`. `refresh.py` strips `[Geo-blocked]`, `[Not 24/7]` and any other `[...]` tag. The user doesn't want them; if a channel works it works, and if not it gets dropped.
- Movie channels: suggest only free, ad-supported channels on official hosts (amagi.tv, otteravision.com, cloudfront or akamai FAST feeds). Never add paid channels (HBO, Cinemax, AXN, Cine Sony, Cinecanal, Golden, De Película, Claro Cinema, Star Channel and the like) carried on bare-IP rebroadcasts.

## Steps

Run these from the repo root. `$S` is the session scratchpad directory and `$K` is `.claude/skills/update-my-cr`.

1. Download the latest upstream Costa Rica list. Don't use `git fetch upstream`; it takes over 2 minutes.
   ```sh
   curl -fsSL --max-time 60 https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cr.m3u -o $S/cr.m3u
   ```
2. Rebuild and test:
   ```sh
   python3 -I $K/refresh.py streams/my-cr.m3u $S/cr.m3u $S/my-cr.new.m3u
   ```
   For each channel already in the list, the script merges in the upstream links. It also re-adds WANTED channels when upstream has them. It tests every link by downloading a real video chunk, retrying failures twice, and keeps only working links. The output is sorted alphabetically, with numbers in number order. Channels that are not Costa Rican keep their existing links.
3. Show the user what changed: links added, links dropped, and channels that came back or disappeared. Then copy the output over `streams/my-cr.m3u` and `~/Downloads/my-cr.m3u`.
4. Remind the user to commit and push so the TV picks up the change, then to refresh the playlist on the TV.

To test any playlist on its own: `python3 -I $K/check.py <file.m3u>`.

## WANTED channels

These were dead on 2026-11-17 and get re-added automatically when upstream has working links for them. Canal 2 and Canal 6 are back, with links from Repretel's site; see below. Still missing: Canal 3 KMK TV, Canal 9, Canal 17 TV Nosara, Cartago Medios TV and Tigo Sports. The list is the `WANTED` variable in `refresh.py`. Remove a channel from it if the user no longer wants it.

## Repretel channels (Canal 2, 4, 6, 11)

The links iptv-org has for these were dead on 2026-11-17. The working links came from Repretel's own live pages, which embed the stream address in their HTML:

```sh
for p in envivo-canal2 envivo-canal4 envivo-canal6 envivo-canal-11; do
  curl -s -A 'Mozilla/5.0' "https://www.repretel.com/$p/" | grep -oE 'https?:\\?/\\?/[^"'"'"' ]*\.m3u8' | sed 's#\\##g' | sort -u
done
```

Canal 11's page is `envivo-canal-11`, with a dash. They play without a referer and top out at 720p. If a Repretel channel dies on a refresh, re-run this to get its current link before dropping it.

## Reading test results

- The Mac's connection is in Costa Rica, so links tagged "[Geo-blocked]" upstream normally play for the user. The tag is stripped from the output.
- `nodename nor servname` means the host no longer exists. Confirm with `dig +short <host> @1.1.1.1`.
- "Not 24/7" channels can be off-air at times, so a single failure may be temporary. The retry covers short glitches.
