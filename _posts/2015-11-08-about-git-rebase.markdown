---
layout: post_with_octocat
title: 小心使用 git rebase
excerpt: 令人糊涂的 git rebase
categories: tech
tags:
- git
date: 2015-11-08 09:49:08
---


**TL;DR 对已发布到远程仓库的分支进行衍合操作(rebase)，会产生重复的提交记录，本文举例描述这个问题。**

git merge 与 git rebase 命令都用来合并代码，如果不需要审查提交记录，两者都可以无脑操作，相互替换；如果要生成有条理的提交记录，前者会记录多条开发分支扰乱视线，因而推荐使用后者。但后者要是使用不当，会生成令人糊涂的提交记录。这点[官方文档](https://git-scm.com/book/zh/v1/Git-%E5%88%86%E6%94%AF-%E5%88%86%E6%94%AF%E7%9A%84%E8%A1%8D%E5%90%88)里有描述，但我嫌它所举例子有点牵强，所以自己举例说明。

要借助 github 模拟多人协作才能说清楚问题（当然你也可以在本地搭建 git server ，我嫌麻烦），所以先新建一个 github 仓库： rebase

克隆到本地 `git clone git@github.com:yiyizym/rebase.git`

切换到 rebase 目录，在本地新建一个文件 initial ，内容如下：

 `created by local user, the first submit on master branch`

添加到暂存区、提交，并推送到远程

继续在本地操作，新建一个分支 dev ： `git checkout -b dev`

新建一个文件 local_dev_branch ，内容如下：

 `created by local user, the first submit on dev branch`

添加到暂存区、提交

继续在 dev 分支操作，修改 initial 文件，在末尾添加一行：

 `add this line by local user, the second submit on dev branch`

添加到暂存区、提交

切换到 github 上面操作，在 master 分支新建一个文件 remote_master_branch ，内容如下：

 `created by remote user, the second submit on master branch`

添加到暂存区、提交

继续在 github master 分支 上操作，修改 initial 文件，在末尾添加一行：

 `add this line by remote user, the third submit on master branch`

添加到暂存区、提交

切换到本地 master 分支，先与远程代码同步，因为可以快进合并，所以用 `git pull`

接下来就是出问题的一步，在本地 master 分支下衍合 dev 分支： `git rebase dev`

提示 initial 文件有冲突，编辑文件，添加到暂存区，提交或者不提交都可以（要是提交了，执行 `git rebase --continue` 就会提示 no changes, 只能用 `git rebase --skip` 跳过），继续执行 `git rebase --continue`

看看 master 分支状态， `git status` ，提示要与远程 master 分支合并

这时要是使用 `git rebase origin/master` ，你会看到两个重复提交：

 `add this line by remote user, the third submit on master branch` ，


**更要命的是， initial 文件里因为自动合并，出现了两行：**

  `add this line by remote user, the third submit on master branch`

这时如果使用 `git pull` ，你会看到两对重复提交（提交描述一样，所作修改一样， hash 值不一样）：

 `created by remote user, the second submit on master branch` / `add this line by remote user, the third submit on master branch` ，


 不过除此之外，不会出现像上面一样的意外

再次推送到远程： `git push origin master`

在 github 上面看提交记录，显示如下：
![commitlog ]({{ site.url }}/assets/rebase.jpg)*commitlog*


**结论**

不要在已发布到远程仓库的分支上进行衍合操作，否则后果可大可小，运气好就只会出现重复提交，运气差的还带有实际伤害。

**参考**

- 本文所举例子 [github 地址](https://github.com/yiyizym/rebase)