# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Destination venv directory can be set through the environment variable `PIPIS_VENV`.
- Destination bin directory can be set through the environment variable `PIPIS_BIN`.

### Changed
- Format `list` output like pip's one.

### Fixed
- Remove venv created in case of inexistant package install attempt

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

[Unreleased]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.2.0...HEAD
[1.1.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.1.0...1.2.0
[1.1.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.0.1...v1.1.0
[1.0.1]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.0.0...v1.0.1
[1.0.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/0c3cc746...v1.0.0
