# Lance Sandino's Homebrew tap

A shared Homebrew tap for my command-line tools on macOS and Linux. Each formula
installs a published release and verifies its SHA-256 checksum.

## Available formulas

| Tool | What it does | Install |
| --- | --- | --- |
| [AWS SSO Profile Sync](https://github.com/LanceSandino/aws-sso-profile-sync) | Keeps AWS CLI profiles in sync with IAM Identity Center accounts and roles, with explicit login, reviewable plans and guarded updates. | `brew install LanceSandino/tap/aws-sso-profile-sync` |
| [SessionSift](https://github.com/LanceSandino/sessionsift) | **No longer maintained** (archived 2026-11-25; [deprecated formula](docs/sessionsift.md)). Local, read-only analysis of Codex and Claude Code sessions. Installs the final 2.1.1 release on macOS Intel and Linux amd64, with no further updates. | `brew install LanceSandino/tap/sessionsift` |

This table lists every formula currently in the tap. More tools can be added as
their releases and installation checks are ready.

## Install and update

Install a tool with its fully qualified command from the table; Homebrew adds the
tap automatically and trusts only that formula. Homebrew does not load formulae
from a tap you have not [trusted](https://docs.brew.sh/Tap-Trust), so to add the
tap separately and browse its formulas, trust it first:

```sh
brew tap LanceSandino/tap
brew trust LanceSandino/tap
brew search LanceSandino/tap/
brew info LanceSandino/tap/aws-sso-profile-sync
```

To trust one formula instead of the whole tap, run
`brew trust --formula LanceSandino/tap/<formula>`.

Update installed tools with `brew update` followed by `brew upgrade <formula>`.
If `brew doctor` reports `lancesandino/tap` as not trusted, for example after
installing with a Homebrew release that did not record trust, run
`brew trust --formula LanceSandino/tap/<formula>` once so upgrades continue.
Remove a tool with `brew uninstall <formula>`. Removing a formula does not remove
the application's configuration or data. Read the linked application docs for
usage, supported platforms, configuration and recovery.

## Maintaining the tap

Keep the catalog above in sync with `Formula/`. New tools belong in their own
formula and need release checksums, license information, supported native targets
and an offline installation test. Keep each tool's release lifecycle separate;
adding a formula must not change another tool's release or source pins.

[AWS SSO Profile Sync validation and formula updates](docs/aws-sso-profile-sync.md)
describes the existing tool-specific pipeline. Those workflows validate only that
formula; another tool needs its own applicable checks before it is added. The
deprecated [SessionSift formula](docs/sessionsift.md) is no longer validated or
updated.

Licensed under [Apache-2.0](LICENSE). Each installed tool has its own license.
