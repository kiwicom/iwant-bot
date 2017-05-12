# Hello everyone!

:star2: If you are reading this document then I'm assuming that you are interested in contributing to the iwant-bot project. This project is made by kiwi.com interns. All contributions are welcome: new use-cases, code, patches, bugfixes, issues, etc. 
This is just set of guidelines, not rules. Use your best judgement, and feel free to propose changes in a pull request.


# Ways to contribute

  - At first, check existing [issues](https://github.com/kiwicom/iwant-bot/issues) and our pull requests and help us with development with your proposed solution or improvement
  - [Create own issue](https://guides.github.com/features/issues/), if you think you have a good idea and let us consider your contribution
  - To report a bug:
      - Open an issue with label "bug" :bug:
      - Describe expected behavior
      - Describe an actual, incorrect behavior
      - It would be great if a pull with possible solution came along with a report
  - You can create your own [pull request](https://help.github.com/articles/creating-a-pull-request/) on [Github](https://github.com/kiwicom/iwant-bot)
### 

### Might be useful

- [coala] - linting and fixing code for all languages
- [tox] - aims to automate and standardize testing in Python

# Code contribution guide
- In this case, you should browse our opened issues, pull requests or use cases
- For every contribution make a pull request and make a comment on issue with your plan of implementing this issue
- Add a tag to the issue 
- Kiwi mentors will work with you on scheme to make sure you are on right track to prevent any wasted work and catch design issues early on
- Implement your issue in your pull request and iterate from there

# Styleguide
### Good Commit Messages
Please,
- Keep commits atomic, it should not describe more than one change
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line short, limit to 50 characters or less
- Limit the every other line to 72 characters or less
- Reference issues and pull requests liberally
- When only changing documentation, include __[ci skip]__ in the commit description
- Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :penguin: `:penguin:` when fixing something on Linux
    * :apple: `:apple:` when fixing something on macOS
    * :checkered_flag: `:checkered_flag:` when fixing something on Windows
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when fixing the CI build
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings
- Keep in mind that commit messages are mainly for the other people, so they should be understandable even after six months
- If you use _git revert_ or undoing commit, default commit message specify which commit you want to revert, but it is not enough to know __why__ you are undoing it, please add more comments to it
#### Example
> ':emoji:' or tag: Short explanation of the commit
>
> Longer explanation which explaining what and why is changed, what bugs or issues were fixed and not too brief further description
> 
> Issue reference - you should use 'Fixes' keyword if your commit fixes a bug, or 'Closes' keyword if your commit 
> adds a feature or enhancement
>
>You should add full URL to the issue  e.g. Closes https://github.com/kiwicom/iwant-bot/issues/13

 [coala]: <https://coala.io/#!/home>
 [circle CI]: <https://circleci.com>
 [tox]: <https://tox.readthedocs.io/en/latest/>