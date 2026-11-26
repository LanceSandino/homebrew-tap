# SessionSift formula (no longer maintained)

SessionSift is no longer maintained. Its repositories were archived on
2026-11-25, and `Formula/sessionsift.rb` is deprecated with
`deprecate! date: "2026-11-25", because: :repo_archived`.

The formula stays on the final release,
[SessionSift 2.1.1](https://github.com/LanceSandino/sessionsift/releases/tag/v2.1.1).
Its release archives remain downloadable, so existing installs keep working and
new installs still succeed. Homebrew prints a deprecation warning. SessionSift
gets no further releases, fixes or formula updates.

Homebrew's warning estimates a disable date one year after deprecation. The
formula stays installable until this tap adds an explicit `disable!` stanza.

SessionSift is a local-only tool: it reads Codex and Claude Code transcripts on
your machine, serves a dashboard on `127.0.0.1` and offers ten read-only MCP
tools. It needs no account or cloud service.

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

Only macOS Intel and Linux amd64 archives are offered; no other targets will be
added. The macOS binary is unsigned and unnotarized; the formula's SHA-256 values
check archive integrity, not publisher identity.

## Maintenance

The tap no longer runs SessionSift install checks or automatic formula updates.
The `sessionsift.yml` and `update-sessionsift.yml` workflows were removed with
the deprecation.
