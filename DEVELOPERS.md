# Developing eprempy

This document contains notes for those who wish to contribute to `eprempy` by modifying the code base. In order to develop `eprempy`, you should fork the respository, edit your forked copy, and submit a pull request for integration with the original repository.

Note that this is a living document and is subject to change without notice.

## Committing to the Repository

### Messages

Commit messages should follow the structure prescribed by the [Angular commit style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines). The exception to that style is that optional message bodies need not be written in imperative present tense. For example, message bodies that read "This new method blonks the flerb with thuzal." and "Create method to blonk the flerb with thuzal." are equally valid.

For convenience, here are the allowed subject types

* feat: A new feature
* fix: A bug fix
* docs: Documentation only changes
* style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
* refactor: A code change that neither fixes a bug nor adds a feature
* perf: A code change that improves performance
* test: Adding missing or correcting existing tests
* chore: Changes to the build process or auxiliary tools and libraries such as documentation generation

