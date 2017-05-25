# iwant-bot
---
## Hello everyone!
- :star2: If you are reading this document then I'm assuming that you are interested in contributing to the __iwant-bot__ project.
- This project is made by Kiwi.com interns. 
- All contributions are welcome: new use-cases, code, patches, bugfixes, issues, etc. 
- This is just set of guidelines, not rules. Use your best judgement, and feel free to propose changes in a pull request.


## Ways to contribute
---
  - At first, check existing [issues](https://github.com/kiwicom/iwant-bot/issues) and our pull requests and help us with development with your proposed solution or improvement
  - [Create own issue](https://guides.github.com/features/issues/), if you think you have a good idea and let us consider your contribution
  - To report a bug:
      - Open an issue with label "bug" :bug:
      - Describe expected behavior
      - Describe an actual, incorrect behavior
      - It would be great if a pull request with possible solution came along with a report
  - You can create your own [pull request](https://help.github.com/articles/creating-a-pull-request/) on [GitHub](https://github.com/kiwicom/iwant-bot)

### Tools we use for linting, testing and fixing code
---
- [coala] - linting and fixing code for all languages
    - You could [install coala](http://docs.coala.io/en/latest/Users/Install.html) on your computer and check different _bears_ on your local machine
    - Every commit is automatically tested on [circle CI] with coala (in development)
- [tox] - aims to automate and standardize testing in Python
    - You could [install tox](https://tox.readthedocs.io/en/latest/install.html) on your computer and test your contribution on your own machine
    - Every commit is automatically tested on [circle CI] with tox


# Code contribution guide
---
- In this case, you should browse our opened issues, pull requests or use cases
- For every contribution make a pull request and make a comment on issue with your plan of implementing this issue
- Add a tag to the issue 
- [Kiwi.com](https://www.kiwi.com/) mentors will work with you on scheme to make sure you are on right track to prevent any wasted work and catch design issues early on
- Implement your issue in your pull request and iterate from there

### Good Commit Messages
---
Please,
- Keep commits atomic, it should not describe more than one change
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line short, limit to 50 characters or less
- Keep the second line empty
- Limit the every other line to 72 characters or less
- Reference issues and pull requests liberally
- Keep in mind that commit messages are __mainly for the other people__, code is way more often read than written
- If you using _git revert_ or undoing commit, default commit message specify which commit you want to revert, but it is not enough to know __why__ you are undoing it, please add more comments and specify why do you undoing commit instead of fixing the bugs and mistakes
#### Example
---
> tag: Short explanation of the commit (max. 50 characters)
> ~~Keep the second line empty~~
> Longer explanation which explaining what and why is changed, what bugs or issues were fixed and not too brief further description (every other line limit to maximum of 72 characters)
> 
> Issue reference - you should use 'Fixes' keyword if your commit fixes a bug, or 'Closes' keyword if your commit 
> adds a feature or enhancement
>
>You should add full URL to the issue e.g. Closes https://github.com/kiwicom/iwant-bot/issues/13

 [coala]: <https://coala.io/#!/home>
 [circle CI]: <https://circleci.com>
 [tox]: <https://tox.readthedocs.io/en/latest/>
