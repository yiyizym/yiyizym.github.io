---
layout: post
title: 理解 Git 工作原理，几篇上好文章
date: 2017-12-16 06:50:10
description: 最近对 Git 又有了更深入的了解，本想用自己的语言解释 Git 原理，但见珠玉在前，没自信做得更好，索性罗列自己看过的好文章
categories: tech
---

**前言**

最近对 Git 又有了更深入的了解，本想用自己的语言解释 Git 原理，但见珠玉在前，没自信做得更好，索性罗列自己看过的好文章。

**一个问题**

Git 只是一个用来管理源码的工具，一般来说，只要了解几个常用命令和遵守团队操作规范，在直到遇上一些奇怪的问题之前，足够应付日常工作了。

但身为程序员总不免遇到难题，我最近就遇到一个： gerrit 不允许同一个 commit 推送两次到远程仓库。

不知道 gerrit 为什么不允许这样做，而我不能因此抛弃 gerrit ，只能想办法绕过去。

我是这样解决问题的，运行下面命令：

```bash
git reset --soft HEAD~
git commit
# 提交之后运行 git push origin HEAD:refs/for/branch_name 就可以推送到远程
```

先不说上面两行代码的原理（因为看完我推荐第二篇文章就知道了），来说说另一个更取巧的解决办法，运行下面这个命令：
```bash
git commit --amend
# 提交之后运行 git push origin HEAD:refs/for/branch_name 就可以推送到远程
```

如果追究为什么会出现“同一个提交两次推送到远程”这种情况，最终你会发现可以在合并分支时禁用[快进合并](https://git-scm.com/book/zh/v2/Git-分支-分支的新建与合并)来避免这个问题：
```bash
git merge other_branch --no-ff
# 之后运行 git push origin HEAD:refs/for/branch_name 就可以推送到远程
```

对不清楚原理的人来说，上面列举的三个操作简直就像是魔法一样，但对知道原理的魔法师来说，这些都只是常规操作而已。

举这个例子只是想说明：理解工具的原理可以帮助我们在遇到麻烦时能找到不止一个解决办法，还能找出问题的根源，从一开始就避免麻烦。

**好文章列表**

Git 是一个非常复杂的工具，一般人要想理解它的工作原理，需要看非常多的资料，以及大量动手实践，这期间极容易走弯路（比如被质量低下的文章误导），导致有反反复复的认知。为了让你能更好更快地理解 Git ，下面就把我自己看过的，觉得比较好的文章（不多，只有四篇），按从表层到深入的顺序罗列出来：

- [图解 Git](https://marklodato.github.io/visual-git-guide/index-zh-cn.html?no-svg)
    
    这是一份清晰易懂的材料，看完之后，你会对 Git 要做的事情有大致的印象： Git 做的事情就是在 工作区、暂存区、仓库（的各个提交）之间操作文件。
- [Git 工具 - 重置揭密](https://git-scm.com/book/zh/v2/Git-工具-重置揭密)
    
    在提及“要了解 Git 原理该读什么书时”，不少人推荐 [Pro Git](https://git-scm.com/book/zh/v2) 。这确实是一本好书：每个概念都有详细的说明和具体的例子，而且是在线免费的。只是如果没有带着特定问题去看的话，可能坚持不到看完。
    
    因为它实在太详细了，很多时候我把它当成一本操作手册。
    
    直到我在第 N 次使用 `git reset` 时，拿不定主意要不要加上 `--soft` 或者 `--mixed` （虽然 [图解 Git](https://marklodato.github.io/visual-git-guide/index-zh-cn.html?no-svg) 有说明 `git reset` 带不同参数下的区别，但也仅限于此，不怪我老记不住），终于下定决心搞清楚这个命令到底做些什么时，点开上面的[链接](https://git-scm.com/book/zh/v2/Git-工具-重置揭密)，从此打开了新世界的大门。

    这一点都不夸张，与其说上面的链接是“重置揭密”，不如说它是“Git 原理浅析”才对。

    相信我，好好看这篇文章，会有巨大收获。

- [使用原理视角看 Git](https://blog.coding.net/blog/principle-of-Git#user-content-2-2-Mi4yIOaaguWtmOWMug=)
- [Git 内部原理](https://git-scm.com/book/zh/v2/Git-内部原理-底层命令和高层命令)

    最后，如果你想搞清楚所谓的暂存区、提交、分支等等概念在翻译成活生生的代码时到底是什么，推荐你看看上面两个链接。
    
    你可以从第一个链接中知道 Git 怎样用 SHA-1 来索引文件内容，以及 Git 是怎样区分文件状态（untracked/modified/both edited/等等）的。

    后面的那个是 Pro Git 上一系列文章的第一篇，算是除了直接读源码之外的终极原理解析了。