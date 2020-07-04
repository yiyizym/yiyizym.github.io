---
layout: post
title: 译文：React 在 Fiber 中使用链表来遍历组件树的原因和方式
date: 2020-07-03 10:20:28
excerpt: 深入 react fiber 系列之一
categories: 
- tech
---

**这是一篇译文，原文[链接][15]**

本文探讨了 React 新的名为 Fiber 的协调器实现中的主要工作循环(work loop)。 它比较并解释了浏览器的调用栈和 React 的 Fiber 架构中的栈的实现之间的差异。

为了教育自己和社区，我在网络技术的逆向工程上面花了很多时间，并写下我的收获。在过去的一年里，我主要专注于 Angular ，我发布了网络上最大的 Angular 出版物--Angular-In-Depth。现在是时候深入研究 React 了。变化检测已经成为我在 Angular 中的主要专业领域，只要有一定的耐心和大量的调试，我希望很快就能在 React 中达到与之相当的水平。

在 React 中，变化检测的机制通常被称为协调或渲染，Fiber 是其最新的实现。由于底层架构的原因，它得以实现许多有趣的功能，如执行非阻塞渲染、根据优先级实施更新和在后台预渲染内容。这些功能在[Concurrent React 理念][1]中被称为时间分割。

除了解决开发者的实际问题外，从工程的角度来看，这些机制的内部实现具有广泛的吸引力。源码中如此丰富的知识，能帮助我们开发者成长。

如果你今天在 Google 上搜索 "React Fiber"，你会在搜索结果中看到不少文章。不过除了 Andrew Clark 的[文章][2]之外，其他的都是很顶层的解释。在本文中，我将参考这篇文章，详细地解释 Fiber 中一些特别重要的概念。看完后你就会有足够的知识来理解这场 Lin Clark 在 ReactConf 2017 上的一个非常好的关于工作循环的[演讲][3]。

建议你去看这场演讲。在此之前要是你花一点时间在源码上，你会对演讲有更深入的理解。

这篇文章是关于 React 的 Fiber 内部实现的[系列文章][4]的开篇。我对 Fiber 内部实现细节的理解大约在 70% 左右，还有三篇关于协调和渲染机制的文章正在书写当中。

让我们开始吧!

## 背景知识

Fiber 的架构有两个主要阶段：协调/渲染和提交。在源码中，协调阶段大多被称为"渲染阶段"。在这个阶段 React 会遍历组件树以及：

- 更新状态和属性
- 调用生命周期钩子函数
- 获取组件的子组件
- 将它们与之前的比较
- 并计算出需要执行的 DOM 更新

所有这些操作在 Fiber 内部被称为 work 。work 类型取决于 React Element 的类型。例如，对于一个类组件， React 需要实例化一个类，而对于一个函数组件，它不需要这样做。如果感兴趣，[这里][5]可以看到 Fiber 中所有与 work 对应的类型。这些操作正是 Andrew 所讲到的：

> 在处理用户界面时会碰到的一个问题是：如果一次性执行太多操作，可能会导致动画掉帧……

"一次性执行"，为什么会出问题呢？

好吧，总的来说，如果 React 要同步遍历整个组件树，并在每个组件上执行相关操作，它的代码逻辑可能会运行超过 16 毫秒，而这将会导致掉帧造成停滞的视觉效果。

以下方法就可以解决问题吗？

> 新近版本的浏览器（还有 React Native）实现了有助于解决这个问题的 API ……

他所说的新 API 是名为 [requestIdleCallback][6] 的全局函数，它通过队列让浏览器在空闲期调用函数。下面是它的调用方式：

```javascript
requestIdleCallback((deadline)=>{
    console.log(deadline.timeRemaining(), deadline.didTimeout)
});
```

如果我现在打开浏览器控制台并执行上面的代码，Chrome 会打印出 `49.9 false` 。这个信息大体上告诉我，我有 49.9 毫秒的时间来做任何我需要做的工作，我还没有用完所有分配的时间，否则 deadline.didTimeout 就会是 true 。请记住，一旦浏览器要执行某些操作，timeRemaining 就会改变，所以应该经常检查这个值。

> 因为 requestIdleCallback 受限制太多，[执行频率不够高][7]，无法实现流畅的 UI 渲染，React 团队不得不[另行实现][8]。

如果我们把 React 在组件上执行的所有操作都放到函数 performWork 中，并使用 requestIdleCallback 来调度这些 work ，我们的代码就会像这样：

```javascript
requestIdleCallback((deadline) => {
    // while we have time, perform work for a part of the components tree
    while ((deadline.timeRemaining() > 0 || deadline.didTimeout) && nextComponent) {
        nextComponent = performWork(nextComponent);
    }
});
```

我们在一个组件上执行 work ，然后返回下一个执行 work 的组件引用。这样做是可行的，但是你不能像[之前实现的协调算法][9]那样，同步处理整个组件树。这就是 Andrew 所提到的问题：

> 为了使用这些 API ，你需要一种方法将渲染工作分解成增量单元。

为了解决这个问题，React 不得不重新实现了遍历树的算法，从依赖内置栈的同步递归模型变成了链接列表和指针的异步模型。而这就是 Andrew 所写的：

> 如果只依靠(内置)调用栈，它会一直执行 work ，直到栈空为止……如果我们可以随意中断调用栈，手动操作栈帧，那不是很好吗？这就是 React Fiber 的目标，Fiber 是专门针对 React 组件的栈的重新实现。你可以把单个 fiber 看作是一个虚拟的栈帧。

这就是我接下要解释的内容。

## 关于堆栈

我想大家应该都很熟悉调用栈的概念。如果程序在断点处暂停运行，在浏览器的调试工具中你能看到直到断点处的调用栈。下面是维基百科上的一些相关引文和图表。

> 在计算机科学中，调用栈是一个堆栈数据结构，它存储了计算机程序的活动子程序的信息……调用栈主要是为了跟踪每个活动子程序在执行完毕后应该返回控制权到何处……调用栈是由堆栈帧组成的……每个堆栈帧对应于对一个尚未结束（以 return 的形式）的子程序的调用。例如，如果一个名为 DrawLine 的子程序目前正在运行，而它被DrawSquare 的子程序调用，那么调用堆栈的顶部可能会像下图那样排列。

![call stack]({{ site.url }}/assets/call_stack.png)*call stack*

为什么堆栈与 React 有关？

正如我们在文章第一部分所定义的那样，React 在协调/渲染阶段行遍历组件树，并为组件执行一些 work 。协调器之前的实现使用的是同步递归模型，依靠内置的栈来遍历树。[官方文档][10]]描述了这个过程，并谈了很多关于递归的内容。

> 默认情况下，当递归一个 DOM 节点的子节点时，React 只是在同一时间遍历新旧两个子节点列表，只要有差异就会记录一处变动。

如果你仔细想想，每次递归调用都会给堆栈增加一帧。而且它以同步执行。假设我们有以下的组件树：

![component_tree]({{ site.url }}/assets/component_tree.png)*component tree*

将节点表示为带有 `render` 函数的对象，你可以把它们看作是组件的实例：

```javascript
const a1 = {name: 'a1'};
const b1 = {name: 'b1'};
const b2 = {name: 'b2'};
const b3 = {name: 'b3'};
const c1 = {name: 'c1'};
const c2 = {name: 'c2'};
const d1 = {name: 'd1'};
const d2 = {name: 'd2'};

a1.render = () => [b1, b2, b3];
b1.render = () => [];
b2.render = () => [c1];
b3.render = () => [c2];
c1.render = () => [d1, d2];
c2.render = () => [];
d1.render = () => [];
d2.render = () => [];
```

React 需要遍历树，并为每个组件执行 work 。简单来说，work 要做的就是记录当前组件的名称，并收集其子代。接下来我们用递归的方式做这些事情。

## 递归遍历

在下面的实现中，遍历树的主要函数叫做 `walk`:

```javascript
walk(a1);

function walk(instance) {
    doWork(instance);
    const children = instance.render();
    children.forEach(walk);
}

function doWork(o) {
    console.log(o.name);
}
```

以下是我们得到的输出：

> a1, b1, b2, c1, d1, d2, b3, c2

如果你对递归不怎么熟悉，可以看看我关于递归的[深度文章][11]。

递归的方法很直观，很适合遍历树。但我们发现，它有局限性。最大的限制是，我们不能将工作分解成增量单元。我们不能在某个组件处暂停工作，稍后再继续。使用这种方法，React 只是不断地迭代，直到处理完所有组件，堆栈为空。

那么 React 是如何实现无递归遍历树的算法呢？它使用的是单链表树遍历算法。它可以暂停遍历，停止堆栈的增长。

## 链表遍历

我很幸运地在[这里][12]找到了 Sebastian Markbåge 概述的算法要点。为了实现这个算法，我们需要一个包含 3 个字段的数据结构:

- child - 第一个子节点的引用
- sibling - 第一个兄弟节点的引用
- return - 指向父节点的引用

在 React 新的协调算法中，带有这些字段的数据结构叫做 Fiber 。本质上说，它就是一个 React Element。React Element 保存了一个 work 队列。关于这一点，我在接下来的文章中会有更多的介绍。

下图展示了通过链表联接的对象的层次结构以及它们之间的连接类型：

![linked_component_tree]({{ site.url }}/assets/linked_component_tree.png)*linked component tree*

让我们先定义一下节点构造函数：

```javascript
class Node {
    constructor(instance) {
        this.instance = instance;
        this.child = null;
        this.sibling = null;
        this.return = null;
    }
}
```

还有接受一个节点数组作为参数并将它们联接在一起的函数。我们要用它来联接 `render` 方法返回的子节点:

```javascript
function link(parent, elements) {
    if (elements === null) elements = [];

    parent.child = elements.reduceRight((previous, current) => {
        const node = new Node(current);
        node.return = parent;
        node.sibling = previous;
        return node;
    }, null);

    return parent.child;
}
```

该函数从最后一个节点开始遍历节点数组，并将它们链接到一个单链表中。它返回对列表中第一个兄弟节点的引用。下面是这个函数使用方式的简单演示:

```javascript
const children = [{name: 'b1'}, {name: 'b2'}];
const parent = new Node({name: 'a1'});
const child = link(parent, children);

// the following two statements are true
console.log(child.instance.name === 'b1');
console.log(child.sibling.instance === children[1]);
```

我们还将实现一个为节点执行一些 work 的 helper 函数。在我们的例子中，它将记录下组件的名称。但除此之外，它还会获取组件的子节点，并将组件和它的子节点链接在一起。

```javascript
function doWork(node) {
    console.log(node.instance.name);
    const children = node.instance.render();
    return link(node, children);
}
```

好了，现在我们准备好实现主要的遍历算法了。这是一个先从父节点开始、深度优先的实现。下面是带上注释的代码：

```javascript
function walk(o) {
    let root = o;
    let current = o;

    while (true) {
        // perform work for a node, retrieve & link the children
        let child = doWork(current);

        // if there's a child, set it as the current active node
        if (child) {
            current = child;
            continue;
        }

        // if we've returned to the top, exit the function
        if (current === root) {
            return;
        }

        // keep going up until we find the sibling
        while (!current.sibling) {

            // if we've returned to the top, exit the function
            if (!current.return || current.return === root) {
                return;
            }

            // set the parent as the current active node
            current = current.return;
        }

        // if found, set the sibling as the current active node
        current = current.sibling;
    }
}
```

虽然这个实现并不是特别难理解，但你可能需要[玩一玩][13]才能摸清它。思路是，我们保留对当前节点的引用，并在访问树的下层节点的过程中对它重新赋值，直到我们到达树的分支的末端，然后我们使用 `return` 指针返回到公共父节点。

如果我们现在查看这个实现的调用栈，我们会看到以下内容：

![walk_call_stack]({{ site.url }}/assets/walk_call_stack.gif)*walk call stack*

正如你所看到的，当我们向下访问树节点的时候，堆栈并没有增长。但如果现在把调试器放到 doWork 函数里，并记录节点名称，我们就会看到以下内容：

![logs_of_walk]({{ site.url }}/assets/logs_of_walk.gif)*logs of walk*

它看起来就像浏览器中的调用栈。通过这种算法，我们有效地用自己的实现取代了浏览器对调用栈的实现。这就是 Andrew 所描述的：

> Fiber 是专门针对 React 组件的栈的再实现。你可以把单个 fiber 看作是一个虚拟的栈帧。

由于我们现在通过保存作为顶层栈帧的节点的引用来控制栈：

```javascript
function walk(o) {
    let root = o;
    let current = o;

    while (true) {
            ...

            current = child;
            ...
            
            current = current.return;
            ...

            current = current.sibling;
    }
}
```

我们可以在任何时候停止遍历，并在稍后恢复到它。这正是我们想要达到的状态，这样我们就能够使用新的 `requestIdleCallback` API 。


## React 的工作循环

这是 React 中实现工作循环的[代码][14]：

```javascript
function workLoop(isYieldy) {
    if (!isYieldy) {
        // Flush work without yielding
        while (nextUnitOfWork !== null) {
            nextUnitOfWork = performUnitOfWork(nextUnitOfWork);
        }
    } else {
        // Flush asynchronous work until the deadline runs out of time.
        while (nextUnitOfWork !== null && !shouldYield()) {
            nextUnitOfWork = performUnitOfWork(nextUnitOfWork);
        }
    }
}
```

正如你所看到的，它能很好地映射到我上面介绍的算法。它将当前 fiber 节点的引用保存在作为顶层栈帧的 `nextUnitOfWork` 变量中。

该算法可以同步遍历组件树，并为树上的每个 fiber 节点执行 work（nextUnitOfWork）。这通常是 UI 事件（点击、输入等等）引起的交互更新的情况（译者注：需要立即响应）。它也可以异步遍历动组件树，在为一个 fiber 节点执行 work 后检查是否还有剩余时间。函数 `shouldYield` 的返回结果取决于 `deadlineDidExpire` 和 `deadline` 变量，这些变量在 React 为 fiber 节点执行 work 时不断被更新。

`peformUnitOfWork` 函数在这里有深入的介绍。

[1]:https://twitter.com/acdlite/status/1056612147432574976
[2]:https://github.com/acdlite/react-fiber-architecture
[3]:https://www.youtube.com/watch?v=ZCuYPiUIONs
[4]:https://indepth.dev/iside-fiber-in-depth-overview-of-the-new-reconciliation-algorithm-in-react/
[5]:https://github.com/facebook/react/blob/340bfd9393e8173adca5380e6587e1ea1a23cefa/packages/shared/ReactWorkTags.js
[6]:https://developers.google.com/web/updates/2015/08/using-requestidlecallback
[7]:https://github.com/facebook/react/issues/13206
[8]:https://github.com/facebook/react/blob/eeb817785c771362416fd87ea7d2a1a32dde9842/packages/scheduler/src/Scheduler.js
[9]:https://reactjs.org/docs/codebase-overview.html
[10]:https://reactjs.org/docs/reconciliation.html
[11]:https://medium.com/angular-in-depth/learn-recursion-in-10-minutes-e3262ac08a1
[12]:https://github.com/facebook/react/issues/7942
[13]:https://stackblitz.com/edit/js-tle1wr
[14]:https://github.com/facebook/react/blob/95a313ec0b957f71798a69d8e83408f40e76765b/packages/react-reconciler/src/ReactFiberScheduler.js
[15]:https://indepth.dev/the-how-and-why-on-React-usage-of-linked-list-in-fiber-to-walk-the-components-tree/

