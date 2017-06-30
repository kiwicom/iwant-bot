# iwant-bot
---
## Hello everyone!
- :star2: If you are reading this document then I'm assuming that you are interested in contributing to the __iwant-bot__ project.
- This project is made by [Kiwi.com] interns. 
- All contributions are welcome: new use-cases, features, patches, bugfixes, issues, etc. 
- This is just a set of guidelines, not rules. 
- Use your best judgement, and feel free to propose changes in a pull request.


## Ways to contribute
---
  - At first, check existing [issues] and our [pull requests] and try to find something that interests you.
  - [Create an issue], if you have an idea and let us consider your contribution.
  - To report a bug:
      - Open an issue with the label "bug" :bug:
      - Describe expected behavior
      - Describe an actual, incorrect behavior
      - Describe steps to reproduce
      - It would be great if a pull request with possible solution came along with the issue/the report
  - You can create your own [pull request](https://help.github.com/articles/creating-a-pull-request/) on [GitHub].
  - If you are __updating__ or __editing__ already existing documents or __creating__ a new one (.gitignore, README.md, etc.), __always__ _create a pull request_.
    - If you are updating or creating larger contribution, you can update related documents, but always make sure that you are __created a single commit__ for each of the documents.
### Tools integrated in CI and running for every commit
---
- Every commit is automatically tested on [CircleCI] with tox and coala.
- [coala] - linting and fixing code for all languages
    - If you want to check you code before the commit, you can [install coala] on your computer and check different enhancement proposals or if there are any errors on your local machine.
- [tox] - aims to automate and standardize testing in Python
    - If you want to check you code before the commit, you can [install tox] on your computer and test your changes.
    


# Code contribution guide
---
- For every contribution make a pull request.
- If there is an issue related with your pull request, please make a comment on issue with your plan of implementation the issue.
- Add a tag to the issue, depending on the situation of your commit (work-in-progress, help-needed, etc.).
- [Kiwi.com](https://www.kiwi.com/) mentors will work with you on scheme to make sure you are on the right track to prevent any wasted work and catch design issues early on.
- Implement the solution of your issue in your pull request and iterate from there.

### Good Commit Messages
---
Please,
- Keep commits atomic, it should __not describe more than one__ change.
- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Keep the first line short, limit to 50 characters or less.
- Keep the second line empty.
- Limit the every other line to 72 characters or less.
- Keep in mind that commit messages are __mainly for the other people__, code is way more often read than written.
- If you are using _git revert_ or undoing commit, default commit message specifies which commit you want to revert, but it is not enough to know __why__ you are undoing it, please add more comments and specify why are you undoing the commit as opposed to fixing the bugs and mistakes.
#### Example
---
> tag: Short explanation of the commit (max. 50 characters)
> ~~Keep the second line empty~~
> __Longer__ explanation which explaining what and why is changed, what bugs or issues were fixed (every other line limit to maximum of 72 characters)
> 
> Issue reference - you should use the 'Fixes' keyword if your commit fixes a bug, or the 'Closes' keyword if your commit 
> adds a feature or enhancement
>
>You should add the full URL to the issue e.g. Closes https://github.com/kiwicom/iwant-bot/issues/13

:tada:

 [Kiwi.com]: <https://www.kiwi.com>
 [install coala]: <http://docs.coala.io/en/latest/Users/Install.html>
 [install tox]: <https://tox.readthedocs.io/en/latest/install.html>
 [GitHub]: <https://github.com/kiwicom/iwant-bot>
 [Create an issue]: <https://github.com/kiwicom/iwant-bot/issues/new>
 [pull requests]: <https://github.com/kiwicom/iwant-bot/pulls>
 [issues]: <https://github.com/kiwicom/iwant-bot/issues>
 [coala]: <https://coala.io>
 [CircleCI]: <https://circleci.com>
 [tox]: <https://tox.readthedocs.io/en/latest>
