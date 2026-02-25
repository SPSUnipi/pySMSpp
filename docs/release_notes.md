# Release Notes

## Upcoming Release

### New Features and Major Changes

* [Avoid shell=true in subprocess and generalize options: add explicit solverconfig option and kwargs to generalize options #73](https://github.com/SPSUnipi/pySMSpp/pull/73)
* [Generalize solver_log #72](https://github.com/SPSUnipi/pySMSpp/pull/72)
* [Convert documentation from Sphinx/RST to MkDocs PR #68](https://github.com/SPSUnipi/pySMSpp/pull/68)
* [Add `plot()` methods to `Variable` and `Block` PR #66](https://github.com/SPSUnipi/pySMSpp/pull/66)
* [Enable functional building of a TSSB block with test PR #64](https://github.com/SPSUnipi/pySMSpp/pull/64)
* [Add TSSB solver PR #58](https://github.com/SPSUnipi/pySMSpp/pull/58)
* [Enable creation of general blocks PR #54](https://github.com/SPSUnipi/pySMSpp/pull/54)
* [Implement Attribute and Dimension as first-class objects PR #51](https://github.com/SPSUnipi/pySMSpp/pull/51)
* [Add TSSB Block structure creation PR #49](https://github.com/SPSUnipi/pySMSpp/pull/49)
* [Add block tree visualization utility PR #39](https://github.com/SPSUnipi/pySMSpp/pull/39)
* [Add is_smspp_installed() to check SMS++ installation PR #41](https://github.com/SPSUnipi/pySMSpp/pull/41)

### Minor Changes and Bug Fixes

* [Improve print_tree: add counts and drop brackets when block_type is missing PR #45](https://github.com/SPSUnipi/pySMSpp/pull/45)
* [Improve docstrings and package-level documentation PR #47](https://github.com/SPSUnipi/pySMSpp/pull/47)
* [Clean smspp tools options PR #48](https://github.com/SPSUnipi/pySMSpp/pull/48)
* [Rename parse_ucblock_solver_log into parse_solver_log PR #55](https://github.com/SPSUnipi/pySMSpp/pull/55)
* [Remove sequential dependency between SMS++ test jobs PR #57](https://github.com/SPSUnipi/pySMSpp/pull/57)
* [Enable empty block_type on Block construction PR #63](https://github.com/SPSUnipi/pySMSpp/pull/63)
* [Use conda package smspp-project for ReadTheDocs builds PR #43](https://github.com/SPSUnipi/pySMSpp/pull/43)
* [Fixed test.yml for macOS PR #38](https://github.com/SPSUnipi/pySMSpp/pull/38)

## Version v0.0.2

### New Features and Major Changes

* [Block constructor PR #5](https://github.com/SPSUnipi/pySMSpp/pull/5)
* [Added DesignNetworkBlock PR #29](https://github.com/SPSUnipi/pySMSpp/pull/29)
* [UC/Investment configs + IntermittentUnitBlock updates PR #27](https://github.com/SPSUnipi/pySMSpp/pull/27)
* [Add hyperarcs PR #21](https://github.com/SPSUnipi/pySMSpp/pull/21)
* [Add Solution object PR #12](https://github.com/SPSUnipi/pySMSpp/pull/12)
* [Add result.solution PR #16](https://github.com/SPSUnipi/pySMSpp/pull/16)
* [Move to highs as default for InvestmentBlock PR #15](https://github.com/SPSUnipi/pySMSpp/pull/15)
* [Enable online logging and resource tracking PR #31](https://github.com/SPSUnipi/pySMSpp/pull/31)

### Minor Changes and Bug Fixes

* [Add SMS++ installation to CI PR #6](https://github.com/SPSUnipi/pySMSpp/pull/6)
* [Add SMS++ in readthedocs workflow PR #9](https://github.com/SPSUnipi/pySMSpp/pull/9)
* [Test windows in CI PR #10](https://github.com/SPSUnipi/pySMSpp/pull/10)
* [Avoid use of match PR #19](https://github.com/SPSUnipi/pySMSpp/pull/19)
* [Update creation of path in windows PR #32](https://github.com/SPSUnipi/pySMSpp/pull/32)
* [Fix CI PR #28](https://github.com/SPSUnipi/pySMSpp/pull/28)

## Version v0.0.1 - Initial Release

### New Features and Major Changes

* Prototype definition of `Attribute`, `Variable`, `Block`, and `SMSNetwork` classes.
* Initial implementation of `SMSPPSolverTool` for UCBlock and InvestmentBlock.
* Documentation with Sphinx and ReadTheDocs.
* Implementation of proper CI with GitHub Actions, including testing on Linux, Windows, and macOS.

## Release Process

* Checkout a new release branch `git checkout -b release-v0.x.x`.
* Finalise release notes at `docs/release_notes.md`.
* Update version number in `pyproject.toml`.
* Open, review, and merge pull request for branch `release-v0.x.x`.
  Make sure to close issues and PRs or the release milestone with it (e.g. closes #X).
  Run `pre-commit run --all-files` locally and fix any issues.
* Update and checkout your local `main` and tag a release with `git tag v0.x.x`, `git push`, `git push --tags`.
  Include release notes in the tag message using the GitHub UI.
