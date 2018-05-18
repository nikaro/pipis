# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Add `-r/--requirement` for the `update` command to allow passing `requirements.txt` file.
- Add `-r/--requirement` for the `install` command to allow passing `requirements.txt` file.

### Changed
- Change output information format fo when package are already/not installed.

## [1.0.1] - 2017-05-17
### Fixed
- Reload `sys.path` and clean it after to avoid issue with "distribution not found".

## [1.0.0] - 2017-05-17
### Added
- Everything.

[Unreleased]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.0.1...HEAD
[1.0.1]: https://gitlab.com/NicolasKAROLAK/pipis/compare/v1.0.0...v1.0.1
[1.0.0]: https://gitlab.com/NicolasKAROLAK/pipis/compare/0c3cc746...v1.0.0
