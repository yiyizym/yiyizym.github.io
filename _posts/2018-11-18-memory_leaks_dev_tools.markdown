---
layout: post
title: javascript 内存泄漏与 Chrome dev tools
date: 2018-11-18 07:07:31
excerpt: 个人认为 前端所谓的 内存泄漏 并不是真正的 内存泄漏
lang: zh_CN
categories: frontend
---

javascript 是一门高级语言，它并不需要程序员（在堆中）手动分配内存，也不需要用完后回收
。
目前 javascript 使用“标记清除”垃圾回收策略，不会有“代码无法触及但又无法回收的内存”的情况，所以我觉得前端并不存在真正的内存泄漏，所谓的内存泄漏只是程序员有意无意地往全局变量中挂载了太多（重复的）变量，如：

- 忘记在变量前面加 `const/let/var` ，导致变量成为全局变量
- 只在 document 中删除了节点，却在 javascrpt 中把这个节点的引用存储在全局变量中(导致 DOM 节点无法被回收)
- 调用 setInterval 后没有 clearInterval ，且在 setInterval 的回调中 DOM 里的节点或者其他 javascript 对象
- 调用 window.console 对象的方法（如 log/error/dir）时传进 DOM 里的节点或者其他 javascript 对象（因为浏览器需要在用户打开控制台时展示这些信息，所以会一直保存这些传进来的信息）
- 将闭包的返回存储在全局变量中

说到闭包跟内存泄漏，有一种很特殊的情况：

```javascript
var theThing = null;
var replaceThing = function () {
  var originalThing = theThing;
  var unused = function () {
    if (originalThing)
      console.log("hi");
  };
  theThing = {
    longStr: new Array(1000000).join('*'),
    someMethod: function () {
      console.log('someMethod');
    }
  };
};
```

可以看到 `someMethod` 并没有引用 `originalThing` ，而引用 `originalThing` 的 `unused` 根本没有返回，但当多次调用 `replaceThing` 时，会内存泄漏（有多个 `theThing` 对象），注释掉 `unused` 或者 `someMethod` 都不会内存泄漏。

`someMethod` 作为函数，它创建了一个新 `scope`（虽然这时里面什么都没有），`unused` 也创建了一个 `scope` ，并且引用了 `parent scope` 的变量 `originalThing`。因为 `unused` 跟 `someMethod` 处在同一个 `parent scope` (即 `replaceThing` 函数) ，这两个函数会共享各自的 `scope` ，因此 `someMethod` 事实上持有 `originalThing` 变量的引用。

我们经常借助 chrome dev tools 分析内存泄漏。首先要知道浏览器的内存分两类：

- 原生内存，指 DOM 节点或绑定在它上面的事件监听器
- javascript heap 

chrome dev tools 中的 `collect garbage` 按钮只会回收第二类，即 javascript heap 的内存。

如果要观察内存在页面整个加载、运行期间的内存占用情况，可以打开 `Performance` 标签页，勾选 `Memory` 后，点击 `Record`，结束之后，可以看到内存（分类）在各个时间点的变化情况。

如果想知道在一顿操作之后，有没有内存泄漏。可以打开 `Memory` 标签页，选择第一项 `heap snapshot` ，在初始状态拍一个快照，一顿操作结束之后，手动点`collect garbage` 按钮，然后拍第二个快照，选择 `Comparison`，对比前后内存的变化。

![heap snapshot comparison]({{ site.url }}/assets/chrome_dev_tools_Comparison.jpg)*heap snapshot comparison*


如果想知道是哪个操作导致内存泄漏，可以打开 `Memory` 标签页，选择第二项 `allocation instrumentation on timeline` ，它会记录每一个操作对应的内存分配，在结束之后，选择某个时间段，可以查看在这个时间段内被分配了内存且直到记录结束时仍然存在的对象。


**参考链接**

- [4 Types of Memory Leaks in JavaScript and How to Get Rid Of Them](https://auth0.com/blog/four-types-of-leaks-in-your-javascript-code-and-how-to-get-rid-of-them/)
- [解决内存问题](https://developers.google.com/web/tools/chrome-devtools/memory-problems/#dom)