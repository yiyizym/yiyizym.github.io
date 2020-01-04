---
layout: post_with_octocat
title: 在 manjaro sublime text 3 中輸入中文
excerpt: "sublime text 很好用，但不能輸入中文就很蛋疼了。水文一篇"
date: 2014-09-23 16:47:38
keywords: manjaro linux, sublime text 3, 中文
categories: tech
---

网上有不少文档说明怎样在 linux sublime text 中输入中文的，比如[这篇](http://c4fun.cn/blog/2013/11/30/linux-sublimetext-chinese/)。本人操作系统是 manjaro linux，按照文档操作能在命令行运行能输入中文的sublime text，但要想在桌面上点击图标运行，就出问题了。

一番折腾之后，终于发现点击图标运行能输入中文sublime text的方法，跟着步骤来：

1. 通过 pacman 安装 sublime text 3 dev 版 和 Fcitx

2. 按照上面提到的那篇文档安装补丁，完成之后就可以在命令行中运行能输入中文的sublime text啦

3. 把 sublime text 放到桌面（不要忘了我们的目标是在桌面上点击运行XD），右键点击找到“编辑启动器”，在“命令”一栏，把原来的`subl3 %F`替换成`bash -c 'LD_PRELOAD=/usr/lib/libsublime_imfix.so /opt/sublime_text_3/sublime_text' %F`，这跟你在命令行中执行的那条命令本质上是一样的，只是两个文件的路径变成了绝对路径。

4. 没有第四步啊，双击打开就OK啦。