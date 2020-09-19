---
layout: post
title: React 在渲染列表时，列表元素的 Key 重复了会怎样？
date: 2020-09-12 10:20:28
excerpt: 除了 warning 还有别的意外惊喜！
lang: zh_CN
categories: 
- frontend
---


如果你在使用 React 渲染列表时，有过不慎产生了重复 key 的经验，你一定会在 console 中看到过以下告警 

> Warning: Encountered two children with the same key, .... Non-unique keys may cause children to be duplicated and/or omitted.

但是 key 重复的 item 也能正常渲染，你或许有疑惑：warning 提到的问题在什么情况下会出现呢？

如果你有疑惑，看看这个[例子][1]。

第一遍渲染时 key 重复的 item ，在第二遍渲染时保留了下来。但这个表现跟 Warning 里说的有点不一样，到底为什么呢？

让我们从源码入手一探究竟吧。

（我得承认对 React 源码不怎么了解，如果你也跟我一样，不妨看看我是怎样找到出问题的源码。）

首先打开开发者工具，点开上面那个 Warning ，查看堆栈信息，可以看到几个有意思的方法名：reconcileChildrenArray / warnOnInvalidKey ，前者似乎是用来决定子数组中要新增加哪些元素、哪些元素要删除；后者当发现不合法的 key 就会报 warning.

![warning_of_repeated_key]({{ site.url }}/assets/warning_of_repeated_key.jpg)*warning of repeated key*

点进去 react-dom.development.js 看 warnOnInvalidKey 的代码，可以看到它里用一个 knowKeys 变量记录 child 的 key 。如果发现 Key 已经存在，就会报 warning 。

![warnOnInvalidKey]({{ site.url }}/assets/warnOnInvalidKey.jpg)*warnOnInvalidKey function*

接下来就在 react-dom.development.js 文件内搜索 knownKeys 这个变量，可惜 React 并没有用它来做其他事情。

一时没想到其他办法，先在报 warning 的地方打个断点调试，看看堆栈变量里有没有蛛丝马迹。

![add_first_breakpoint]({{ site.url }}/assets/add_first_breakpoint.jpg)*add_first_breakpoint*

你会发现程序只会在第一次渲染时运行这个 warning，第二遍渲染时不会触发这个断点。

因为我们要研究第二遍渲染时的问题，因此这个 warning 的价值不高，不得不换个思路了。

在第二遍渲染时，前几个元素被移除了，程序肯定执行了删除操作，我们可以用 'remove' 或者 'unmount' 关键字在 react-dom.development.js 里搜索一下，看看会不会有什么发现。 搜出了 61 个 'remove' ，而 'unmount' 出现在 46 个地方。把它们都快速看一遍，在觉得可疑的地方打个断点，以 remove 为例。

打好断点之后再刷新一遍页面。果然命中了其中一个，可以看到这时页面的前几个元素还没有被移除。只要一步步执行下去，就能定位问题。

![first remove breakpoint]({{ site.url }}/assets/first_remove_breakpoint.jpg)*first remove breakpoint*

点 step over next function call(或者按 F10)，直到看到第一个元素被移除，再继续点 step over next function call 好几遍，不久就会发现程序又回到刚刚上面那个断点，很快第二个元素就会被移除。

![before second element remove]({{ site.url }}/assets/before_second_element_remove_breakpoint.jpg)*before second element remove breakpoint*

仔细看这个断点的上下文，会发觉它在一个 while(true) 循环内，这个循环用来移除第一到第四个元素。可以猜想而到了第五个元素时，它就跳出了循环，在所有可能跳出循环的地方都打个断点。

![all possible return]({{ site.url }}/assets/all_possible_return.jpg)*all possible return*

然后点 Resume Script execution (或者按 F8)，让程序直接运行到下一个断点。当程序要跳出循环时，再一步步执行，看后面做了些什么事。

原来外层还有一个 while(nextEffect !== null) 循环。因为在循环内部不断地将 nextEffect 重新赋值： nextEffect = nextEffect.nextEffect 。可以想像第四个元素的 nextEffect.nextEffect 并没有指向第五个元素的 nextEffect ，而是指向 null ，所以跳出了循环。

![set_next_effect_1]({{ site.url }}/assets/set_next_effect_1.jpg)*set_next_effect_1*
![set_next_effect_2]({{ site.url }}/assets/set_next_effect_2.jpg)*set_next_effect_2*

全局搜 nextEffect.nextEffect ，发现有 8 个地方，全都打上断点，然后刷新页面。程序触发一个断点，但是无论从断点的堆栈，还是断点之后的代码上下中都没有发现跟第四个元素相关的信息。

![nextEffect breakpoint]({{ site.url }}/assets/nextEffect_breakpoint.jpg)*nextEffect breakpoint*

有没有可能在设置第四个元素的 nextEffect.nextEffect 时，用的不是 nextEffect.nextEffect = null ，而是 xxx..nextEffect = null 呢？

试着用 '.nextEffect = null' 去搜索，发现有 9 个地方，在可疑的地方都打上断点，刷新页面。触发了一个断点，而是发现一个很有意义的变量： childToDelete 。React 是怎么决定哪些 child 应该被要 delete 的呢？

![nextEffect_childToDelete]({{ site.url }}/assets/nextEffect_childToDelete.jpg)*nextEffect_childToDelete*


往上一个堆栈，就能发现一个叫 existingChildren 的变量，而这个变量由 mapRemainingChildren 方法计算得来。如无意外，只要看这个方法的内部实现就能定位问题原因了。

![existingChildren]({{ site.url }}/assets/existingChildren.jpg)*existingChildren*

在调用 mapRemainingChildren 的代码打断点，刷新页面。点 Step into(或者按 F11) 进去 mapRemainingChildren 内部，

![mapRemainingChildren]({{ site.url }}/assets/mapRemainingChildren.jpg)*mapRemainingChildren*
![mapRemainingChildren_inner]({{ site.url }}/assets/mapRemainingChildren_inner.jpg)*mapRemainingChildren_inner*

程序会从 currentFirstChild 开始，通过 existingChild.key ，用 Map 实例（existingChildren）记录下 existingChild ，并通过赋值 existingChild = existingChild.sibling ，不断遍历 existingChild 。
![mapRemainingChildren_1]({{ site.url }}/assets/mapRemainingChildren_1.jpg)*mapRemainingChildren_1*
![mapRemainingChildren_2]({{ site.url }}/assets/mapRemainingChildren_2.jpg)*mapRemainingChildren_2*

问题就出在这里：
因为第四个元素的 key 跟第五个元素的 key 都是 4 ，所以 existingChildren 中第四个元素会被第五个元素覆盖。被移除的是第五个元素，第四个元素被保留下来。

为了证明这点。可以在列表子元素中新增加一个属性： data-key ，属性值就是当前的元素在数组中的 index 。可以在[这里][2]实际运行。

比较第一遍渲染时的 data-key ，跟第二遍渲染时的 data-key ，可以确定第五个元素被移除，还保留下来的是第四个元素。


![react_duplicated_data_key_1]({{ site.url }}/assets/react_duplicated_data_key_1.jpg)*react_duplicated_data_key_1*
![react_duplicated_data_key_2]({{ site.url }}/assets/react_duplicated_data_key_2.jpg)*react_duplicated_data_key_2*


用 React 渲染列表时， key 重复看上去只报 warning ，实际真的会引发问题，所以千万不要不当一回事。

[1]:https://codesandbox.io/s/suspicious-wilson-7r3ps
[2]:https://codesandbox.io/s/wonderful-galileo-jj1zt?file=/src/App.js