# SessionSift formula maintenance

[SessionSift 2.1.0](https://github.com/LanceSandino/sessionsift/releases/tag/v2.1.0)
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

The formula's offline test uses a disposable `HOME`, `SESSIONSIFT_HOME`,
`CODEX_HOME` and `CLAUDE_HOME`, so it never reads real transcripts. Release
qualification additionally installs the exact archives in a copied Homebrew
prefix, starts and stops the service, upgrades from the previous candidate, rolls
back, and exercises all ten MCP tools against synthetic transcripts.
