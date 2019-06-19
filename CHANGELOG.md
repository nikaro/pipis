# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0]
### Added
- Add `search` command, to search packages on PyPI.

### Changed
- Complete rewrite with argparse (removing depency to Click)

### Removed
- The `list` command, it had no real purpose
- The possibility to install multiple package at once, will be re-added later
- The possibility to upgrade all package with `pipis update`, will be re-added later

## [1.5.0]
### Added
- Add `-I` or `--ignore-installed` option on `install` and `update` commands.
- Add `-U` or `--upgrade` option on `install` command.

### Changed
- Move some portion of code into separate functions to make the code easier to read.
- Updating an uninstalled package will install it, instead of failing.
- While creating symlinks, if the target already exists it will be replaced, instead of failing.

### Fixed
- Fix some linting warnings.

## [1.4.0]
### Added
- Install option `-s` or `--system-site-packages` to give access to system site-packages to venv.
- Allow to specify package version (ex: `ansible==2.4.0`).
- Add a package into a package's venv with `-d` or `--dependency` option.
- Add `-v` or `--verbose` option on `install` and `update` commands.

## [1.3.1]
### Fixed
- Refactor environment variable retrieval.

## [1.3.0]
### Added
- Destination venv directory can be set through the environment variable `PIPIS_VENV`.
- Destination bin directory can be set through the environment variable `PIPIS_BIN`.

### Changed
- Format `list` output like pip's one.

### Fixed
- Remove venv created in case of inexistant package install attempt.
- Raise error when the package is a library (has no user script).
- Raise error when the symlink destination already exists.
- Raise error when trying to update an inexistant package.

## [1.2.0]
### Added
- Add `freeze` command to output installed packages in requirements format.
- Add command to show pipis version.

### Changed
- Show version beside package name in `list` command.
- Improve existing and add new help texts.
- Add short from `-y` for `--yes` argument.
- Factorize duplicate code.

### Fixed
- Fix pep8 and pylint warnings.

## [1.1.0] - 2018-05-18
### Added
- Add `-r/--requirement` for the `remove` command to allow passing `requirements.txt` file.
- Add `-r/--requirement` for the `update` command to allow passing `requirements.txt` file.
- Add `-r/--requirement` for the `install` command to allow passing `requirements.txt` file.

### Changed
- Change output information format fo when package are already/not installed.

## [1.0.1] - 2018-05-17
### Fixed
- Reload `sys.path` and clean it after to avoid issue with "distribution not found".

## [1.0.0] - 2018-05-17
### Added
- Everything.

[Unreleased]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v2.0.0...HEAD
[2.0.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.5.0...v2.0.0
[1.5.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.4.0...v1.5.0
[1.4.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.3.1...v1.4.0
[1.3.1]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.3.0...v1.3.1
[1.3.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.2.0...v1.3.0
[1.2.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.1.0...1.2.0
[1.1.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.0.1...v1.1.0
[1.0.1]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.0.0...v1.0.1
[1.0.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/0c3cc746...v1.0.0
