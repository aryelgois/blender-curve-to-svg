# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

### Changed
- Bump Blender version

### Deprecated

### Removed

### Fixed
- Use matrix multiplication operator — _see [PEP 465]_

### Security


## [0.0.2] - 2019-05-04

### Added
- [Changelog](CHANGELOG.md)
- [License](LICENSE)
- [Readme](README.md)
- Links for GitHub repository
- Scale property

### Changed
- Renamed `export_svg.py` to `curve_to_svg.py`
- Better messages when having other objects selected
- Refactor `col_to_hex()`
- Rename `prettify()` to `pretty_xml()`
- Rewrite `DATA_OT_CurveExportSVG`
  - Split logic in more methods

### Fixed
- Typos and descriptions
- Viewbox is now properly defined


## [0.0.1] - 2017-01-28

### Added
- Initial `export_svg.py` script


[Unreleased]: https://github.com/aryelgois/blender-curve-to-svg/compare/v0.0.2...develop
[0.0.2]: https://github.com/aryelgois/blender-curve-to-svg/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/aryelgois/blender-curve-to-svg/releases/tag/v0.0.1

[PEP 465]: https://www.python.org/dev/peps/pep-0465/
