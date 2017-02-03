---
layout: post
title: 方法只做一件事
date: 2017-01-15 10:31:26
description: clean code 给我的启发
categories: tech
tags:
- clean code
---

当职业程序员有两年多，算上休息时写的，代码量也不算少了，但每次有机会回望自己写的代码，总觉得与别人写得好的那些代码有差距，别人写的读起来短、易懂。

我知道方法越短越好，但一旦自己写起短代码来，就导致一个简单的功能，实现代码会嵌套四/五层，曾经因此被人说过“代码分得太细”，我自己读着的感觉也不好：虽然方法都短小，但不易懂。

后来我逐渐归纳出一个组织代码的想法：处于同一抽象层级的代码应该放在一起，不在同一抽象层级的代码就应该分开写。

我想，这一个想法跟本文题目的意义是一样的。

“方法只做一件事”这个论调很常见，在程序员界很政治正确，但落到实处，首先就会遇到这个问题：怎样才算是一件事？

举个例子，要实现一个“把大象放进冰箱”的方法，方法内部大概可以这样写：
```
  def put_elephant_in_fridge:
    
    open_fridge
    put_elephant_in
    close_fridge

  end
```
上面的 `put_elephant_in_fridge` 方法，做了一件事还是三件事？显然会数数的人都会说是三件事，但我会说这是“一件事”。首先，这三件事都处在同一个抽象层级，然后，这三件事都处在 `put_elephant_in_fridge` 方法往下一级的抽象层级上。

问题又来了，怎样判别方法是否处在同一个抽象层级呢？接着上面的例子，看另一种实现：
```
  def put_elephant_in_fridge:
    
    figure_out_the_volume_of_fridge

    if fridge_not_found or fridge_not_big_enough
      buy_a_fridge
      open_fridge
    else
      open_fridge

    chop_elephant
    full_fill_fridge

    close_fridge

  end
```
上面的方法，前几行是确保找到足够大的冰箱， `chop_elephant` 和 `full_fill_fridge` 描述怎样处理大象，怎样把大象塞进冰箱。显然，这些方法相对 `close_fridge` 来说都是实现细节，它们都不在同一个抽象层级：第一层级是 `close_fridge` ，第二层是 `chop_elephant` 和 `full_fill_fridge` ，最下层的是前面几行代码。写代码的时候应该像第一段代码那样隔离不同层级的抽象，隐藏实现细节。

现实情况下，要求程序员一边实现功能，一边把代码按不同抽象层级安放好或许有点强人所难，可以先后做这两件事。关键是要做，只有这样才能写出好代码。

“方法只做一件事”，出自「clean code」。如果在我刚当程序员的时候看这本书，或许不会像如今有这么大收获，那时写过的代码少，遇到的问题也少，有过困惑和思考的就更少了；现在的我，看书的每一节都能联系到自己一直以来遇到过的、思考过的问题，这些问题有的已经有了模糊答案，有的想不明白，不论怎样书中的解释总能带给我新的启发。

“方法只做一件事”就是如此。