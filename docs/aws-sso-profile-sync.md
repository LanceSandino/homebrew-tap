# AWS SSO Profile Sync formula maintenance

[AWS SSO Profile Sync 2.1.0](https://github.com/LanceSandino/aws-sso-profile-sync/releases/tag/v2.1.0)
is published and installable from this public tap. Native candidate and actual
public installation checks passed on Linux amd64/arm64 and macOS Intel/ARM.

```sh
brew install LanceSandino/tap/aws-sso-profile-sync
brew test LanceSandino/tap/aws-sso-profile-sync
```

The formula installs the published CLI archive, with no GUI, service or AWS CLI
dependency. Its offline test uses disposable HOME and explicit AWS paths. Real
AWS acceptance is recorded in the
[application's tagged acceptance record](https://github.com/LanceSandino/aws-sso-profile-sync/blob/v2.1.0/.github/release-acceptance.json);
tap CI never accesses real AWS or personal configuration.

## Validation

`candidate.yml` builds isolated application archives, generates and audits a
formula, verifies exact SemVer parsing, and tests native installation through a
loopback server. `APP_SOURCE_REF` pins the reviewed application commit; a manual
`app_ref` can select another candidate. Set the variable explicitly rather than
depending on the workflow's legacy review-branch fallback.

`published.yml` verifies all four public release archives, combined checksums,
native/real-acceptance metadata, the exact generated formula and tag-to-source
binding before installing the native public archive. `PUBLISHED_SOURCE_SHA` pins
the published tag's exact commit. Its version comes from `VERSION` in the
application checkout pinned by `APP_SOURCE_REF`; an optional manual `version`
must match. For an update, change both source variables to the reviewed release
commit and regenerate the formula; no workflow version edit is needed.

Published validation runs for README, documentation, formula, verifier, workflow
and `test_published*.py` changes on pull requests and branch pushes. All four native
installation checks must pass on the pull request before merge. Manual dispatch
is available for additional validation.

Tag API checks use an optional ephemeral job token restricted to the exact
application tag routes. Public assets remain anonymous; redirects strip
authentication and errors redact token data. Checkout credentials are not
persisted. Installation tests remove inherited AWS variables and use runner-owned
HOME, cache and configuration paths. CI does not publish, push, tag, merge or
automatically update formulas.

## Formula updates

Use the application repository's `scripts/homebrew.py` with the release's four
verified archives and `SHA256SUMS`. Review `Formula/aws-sso-profile-sync.rb` and
keep generated URLs and hashes exact. Publish matching assets before merging;
never substitute placeholder hashes. Run candidate and published native checks,
plus `brew style`, strict audit, installation and the offline formula test.
