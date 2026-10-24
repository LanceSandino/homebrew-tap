# SessionSift formula maintenance

[SessionSift 2.1.1](https://github.com/LanceSandino/sessionsift/releases/tag/v2.1.1)
is a local-only tool: it reads Codex and Claude Code transcripts on your machine,
serves a dashboard on `127.0.0.1` and offers ten read-only MCP tools. It needs no
account or cloud service.

```sh
brew install LanceSandino/tap/sessionsift
sessionsift doctor
brew services start sessionsift
sessionsift web
```

The service runs `sessionsift start` as your user, not root. Stopping or
uninstalling keeps your library in `~/.sessionsift`:

```sh
brew services stop sessionsift
brew uninstall sessionsift
```

## Platforms and trust

Only macOS Intel and Linux amd64 archives are offered. Apple Silicon and Linux
ARM64 are deferred until they pass native testing. The macOS binary is unsigned
and unnotarized; the formula's SHA-256 values check archive integrity, not
publisher identity.

## Validation

`sessionsift.yml` runs on every formula change, on the update branches and
weekly. On Linux amd64 and macOS Intel runners it checks the formula's
checksums against the release's published `SHA256SUMS`, then runs
`brew style`, `brew audit --strict`, `brew install`, `brew test` and
`sessionsift doctor` in a disposable home before uninstalling. The formula test
never reads real transcripts.

## Updates

`update-sessionsift.yml` runs daily and on demand. It downloads the latest
[SessionSift release](https://github.com/LanceSandino/sessionsift/releases),
regenerates `Formula/sessionsift.rb` with that release's `scripts/homebrew.py`
(which refuses archives whose checksums or build metadata do not match), and
opens a pull request on `update/sessionsift-<version>`. It then starts the
install test on that branch. Merge the pull request once the checks pass.

The formula is generated, so change `scripts/homebrew.py` in the SessionSift
repository rather than editing it here.
