---
layout: post
title: 译文：react fiber 如何以及为什么使用链表遍历组件
date: 2019-11-13 10:20:28
excerpt: 深入 react fiber 系列之一
categories: 
- tech
---

**这是一篇译文，原文[链接](https://indepth.dev/the-how-and-why-on-reacts-usage-of-linked-list-in-fiber-to-walk-the-components-tree/)**


This article explores the main the work loop in React’s new reconciler implementation called Fiber. It compares and explains the differences between browser's call stack and the implementation of the stack in React's Fiber architecture.

本文探讨了React新的名为Fiber的调和器实现中的主要*工作循环*。 它比较并解释了浏览器的调用栈和React的Fiber架构中的栈的实现之间的差异。

To educate myself and the community, I spend a lot of time reverse-engineering web technologies and writing about my findings. In the last year, I’ve focused mostly on Angular sources which resulted in the biggest Angular publication on the web — Angular-In-Depth. Now the time has come to dive deep into React. Change detection has become the main area of my expertise in Angular, and with some patience and a lot of debugging, I hope to soon achieve that level in React.

为了教育自己和社区，我花了很多时间对网络技术进行逆向工程，并写下我的发现。在过去的一年里，我主要专注于*Angular源*，这*导致了*网络上最大的Angular出版物--Angular-In-Depth。现在是时候深入研究React了。变更检测已经成为我在Angular中的主要专业领域，只要有一定的耐心和大量的调试，我希望很快就能在React中达到这个水平。

In React, the mechanism of change detection is often referred to as reconciliation or rendering, and Fiber is its newest implementation. Due to the underlying architecture, it provides capabilities to implement many interesting features like performing non-blocking rendering, applying updates based on the priority and pre-rendering content in the background. These features are referred to as time-slicing in the Concurrent React philosophy.

在React中，变化检测的机制通常被称为*调和*或渲染，Fiber是其最新的实现。由于底层架构的原因，它提供了实现许多有趣功能的能力，如执行非阻塞渲染、根据优先级应用更新和在后台预渲染内容。这些功能在Concurrent React理念中被称为时间分割。

Besides solving real problems of application developers, the internal implementation of these mechanisms has a wide appeal from the engineering perspective. There’s such a wealth of knowledge in the sources that will help us grow as developers.

除了解决应用开发者的实际问题外，从工程的角度来看，这些机制的内部实现具有广泛的吸引力。在源头上有如此丰富的知识，将有助于我们开发者的成长。

If you Google “React Fiber” today you’re going to see quite a lot articles in the search results. All of them, though, except for the notes by Andrew Clark are pretty high-level explanations. In this article, I’ll refer to this resource and provide an elaborate explanation for some particularly important concepts in Fiber. Once we’ve finished, you’ll have enough knowledge to understand the work loop representation from a very good talk by Lin Clark at ReactConf 2017. That’s the one talk you need to see. But it’ll make a lot more sense to you after you’ve spent a little time in the sources.

如果你今天在Google上搜索 "React Fiber"，你会在搜索结果中看到不少文章。不过除了Andrew Clark的笔记之外，其他的都是很高级别的解释。在本文中，我将参考这个资源，对Fiber中一些特别重要的概念进行详细的解释。一旦我们完成了，你就会有足够的知识来理解工作循环的表示，来自Lin Clark在ReactConf 2017上的一个非常好的演讲。这是你需要看的一个演讲。但在你花了一点时间在源头上之后，你会觉得更有意义。

This post opens a series on React’s Fiber internals. I’m about 70% through understanding the internal details of the implementation and have three more articles on reconciliation and rendering mechanism in the works.


这篇文章开启了关于React的Fiber内部的系列文章。我对内部实现细节的理解已经完成了70%左右，还有三篇关于调和和渲染机制的文章正在编写中。

Let’s get started!

让我们开始吧!


Setting the background

**准备背景知识**

Fiber’s architecture has two major phases: reconciliation/render and commit. In the source code the reconciliation phase is mostly referred to as the “render phase”. This is the phase when React walks the tree of components and:

updates state and props,
calls lifecycle hooks,
retrieves the children from the component,
compares them to the previous children,
and figures out the DOM updates that need to be performed.

Fiber的架构有两个主要阶段：调和/渲染和提交。在源代码中，调和阶段大多被称为 "渲染阶段"。这个阶段是React走组件树和。

更新状态和道具。
调用生命周期钩子。
从组件中检索子代。
将他们与之前的孩子进行比较。
并计算出需要执行的DOM更新。

All these activities are referred to as work inside Fiber. The type of work that needs to be done depends on the type of the React Element. For example, for a Class Component React needs to instantiate a class, while it doesn't do it for a Functional Component. If interested, here you can see all types of work targets in Fiber. These activities are exactly what Andrew talks about here:

所有这些活动都被称为Fiber内部的工作。需要做的工作类型取决于React元素的类型。例如，对于一个类组件，React需要实例化一个类，而对于一个功能组件，它不需要这样做。如果有兴趣，这里可以看到Fiber中所有类型的工作目标。这些活动正是Andrew在这里讲到的。

When dealing with UIs, the problem is that if too much work is executed all at once, it can cause animations to drop frames…

在处理用户界面时，问题是如果一次性执行太多工作，可能会导致动画掉帧...。

Now what about that ‘all at once’ part? Well, basically, if React is going to walk the entire tree of components synchronously and perform work for each component, it may run over 16 ms available for an application code to execute its logic. And this will cause frames to drop causing stuttering visual effects.

现在，那个 "一次全部 "的部分呢？好吧，基本上，如果React要同步走过整个组件树，并为每个组件执行工作，它可能会运行超过16毫秒的应用程序代码执行其逻辑。而这将会导致掉帧造成停滞的视觉效果。

So this can be helped?

所以，这可以帮助？

Newer browsers (and React Native) implement APIs that help address this exact problem…

较新的浏览器（和React Native）实现了有助于解决这个确切问题的API...

The new API he talks about is the requestIdleCallback global function that can be used to queue a function to be called during a browser’s idle periods. Here’s how you would use it by itself:

他谈到的新API是requestIdleCallback全局函数，可以用来排队在浏览器空闲期调用一个函数。下面是你自己如何使用它。

```javascript
requestIdleCallback((deadline)=>{
    console.log(deadline.timeRemaining(), deadline.didTimeout)
});
```

If I now open the console and execute the code above, Chrome logs 49.9 false. It basically tells me that I have 49.9 ms to do whatever work I need to do and I haven’t yet used up all allotted time, otherwise the deadline.didTimeout would be true. Keep in mind that timeRemaining can change as soon as a browser gets some work to do, so it should be constantly checked.

如果我现在打开控制台并执行上面的代码，Chrome会记录49.9 false。它基本上告诉我，我有49.9毫秒的时间来做任何我需要做的工作，我还没有用完所有分配的时间，否则deadline.didTimeout就会是true。请记住，一旦浏览器有工作要做，timeRemaining就会改变，所以应该经常检查它。

requestIdleCallback is actually a bit too restrictive and is not executed often enough to implement smooth UI rendering, so React team had to implement their own version.

requestIdleCallback其实限制性太强，执行频率不够高，无法实现流畅的UI渲染，所以React团队不得不实现自己的版本。

Now if we put all the activities Reacts performs on a component into the function performWork, and use requestIdleCallback to schedule the work, our code could look like this:

现在，如果我们把Reacts在组件上执行的所有活动都放到函数 performWork中，并使用 requestIdleCallback来安排工作，我们的代码就会像这样。

```javascript
requestIdleCallback((deadline) => {
    // while we have time, perform work for a part of the components tree
    while ((deadline.timeRemaining() > 0 || deadline.didTimeout) && nextComponent) {
        nextComponent = performWork(nextComponent);
    }
});
```

We perform the work on one component and then return the reference to the next component to process. This would work, if not for one thing. You can’t process the entire tree of components synchronously, as in the previous implementation of the reconciliation algorithm. And that’s the problem Andrew talks about here:

我们在一个组件上执行工作，然后将引用返回给下一个组件进行处理。如果不是因为一件事，这样做是可行的。你不能像之前实现的调和算法那样，同步处理整个组件树。而这就是Andrew在这里谈到的问题。

in order to use those APIs, you need a way to break rendering work into incremental units

为了使用这些API，你需要一种将渲染工作分解成增量单位的方法。

So to solve this problem, React had to re-implement the algorithm for walking the tree from the synchronous recursive model that relied on the built-in stack to an asynchronous model with linked list and pointers. And that’s what Andrew writes about here:

所以为了解决这个问题，React不得不重新实现了走树的算法，从依赖内置栈的同步递归模型变成了链接列表和指针的异步模型。而这就是Andrew在这里写的内容。

If you rely only on the [built-in] call stack, it will keep doing work until the stack is empty…Wouldn’t it be great if we could interrupt the call stack at will and manipulate stack frames manually? That’s the purpose of React Fiber.Fiber is re-implementation of the stack, specialized for React components. You can think of a single fiber as a virtual stack frame.

如果只依靠[内置的]调用栈，它会一直做工作，直到栈空为止......如果我们可以随意中断调用栈，手动操作栈帧，那不是很好吗？这就是React Fiber.Fiber的目的，Fiber是栈的再实现，专门针对React组件。你可以把一根光纤看作是一个虚拟的栈帧。

And that’s what I’m going to explain now.

这就是我现在要解释的。

A word about the stack

关于堆栈

I assume you’re all familiar with the notion of a call stack. This is what you see in your browser’s debugging tools if you pause code at a breakpoint. Here are a few relevant quotes and diagrams from Wikipedia:

我想大家应该都很熟悉调用栈的概念。如果你在断点处暂停代码，你在浏览器的调试工具中看到的就是这个概念。下面是维基百科上的一些相关引文和图表。

In computer science, a call stack is a stack data structure that stores information about the active subroutines of a computer program… the main reason for having call stack is to keep track of the point to which each active subroutine should return control when it finishes executing… A call stack is composed of stack frames… Each stack frame corresponds to a call to a subroutine which has not yet terminated with a return. For example, if a subroutine named DrawLine is currently running, having been called by a subroutine DrawSquare, the top part of the call stack might be laid out like in the adjacent picture.

在计算机科学中，调用栈是一个堆栈数据结构，它存储了计算机程序的活动子程序的信息......拥有调用栈的主要原因是为了跟踪每个活动子程序在执行完毕后应该返回控制权的点......调用栈是由堆栈帧组成的......每个堆栈帧对应于对一个尚未以返回结束的子程序的调用。例如，如果一个名为DrawLine的子程序目前正在运行，已经被DrawSquare的子程序调用，那么调用堆栈的顶部可能会像下图那样排列。

Why is the stack relevant to React?

为什么堆栈与React有关？

As we defined in the first part of the article, Reacts walks the components tree during the reconciliation/render phase and performs some work for components. The previous implementation of the reconciler used the synchronous recursive model that relied on the built-in stack to walk the tree. The official doc on reconciliation describe this process and talk a lot about recursion:

正如我们在文章第一部分所定义的那样，Reacts在调和/重构阶段行走组件树，并为组件执行一些工作。调和器之前的实现使用的是同步递归模型，依靠内置的栈来走树。调和的官方文档描述了这个过程，并谈了很多关于递归的内容。

By default, when recursing on the children of a DOM node, React just iterates over both lists of children at the same time and generates a mutation whenever there’s a difference.

默认情况下，当递归一个DOM节点的子节点时，React只是在同一时间对两个子节点列表进行迭代，只要有差异就会产生突变。

If you think about it, each recursive call adds a frame to the stack. And it does so synchronously. Suppose we have the following tree of components:

如果你仔细想想，每次递归调用都会给堆栈增加一帧。而且它是同步进行的。假设我们有以下的组件树。

Represented as objects with the render function. You can think of them as instances of components:

用渲染函数表示为对象。你可以把它们看作是组件的实例。

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

React needs to iterate the tree and perform work for each component. To simplify, the work to do is to log the name of the current component and retrieve its children. Here’s how we do it with recursion.

React需要迭代树，并为每个组件执行工作。简单来说，要做的工作就是记录当前组件的名称，并检索其子代。下面是我们如何用递归的方式来完成。

Recursive traversal

递归遍历

The main function that iterates over the tree is called walk in the implementation below:

在下面的实现中，在树上迭代的主要函数叫做walk。

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

Here’s the output we’re getting:

这是我们得到的输出。

a1, b1, b2, c1, d1, d2, b3, c2

If you don’t feel confident with recursions, check out my in-depth article on recursion.

如果你对递归没有信心，可以看看我关于递归的深度文章。

A recursive approach is intuitive and well-suited for walking the trees. But as we discovered, it has limitations. The biggest one is that we can’t break the work into incremental units. We can’t pause the work at a particular component and resume it later. With this approach React just keeps iterating until it processed all components and the stack is empty.

递归的方法很直观，很适合走树。但我们发现，它有局限性。最大的限制是，我们不能将工作分解成增量单位。我们不能在某个组件处暂停工作，稍后再继续。使用这种方法，React只是不断地迭代，直到处理完所有组件，堆栈为空。

So how does React implement the algorithm to walk the tree without recursion? It uses a singly linked list tree traversal algorithm. It makes it possible to pause the traversal and stop the stack from growing.

那么React是如何实现无递归走树的算法呢？它使用的是单链路列表树遍历算法。它可以暂停遍历，停止堆栈的增长。

Linked list traversal
链接列表遍历

I was lucky to find the gist of the algorithm outlined by Sebastian Markbåge here. To implement the algorithm, we need to have a data structure with 3 fields:

child — reference to the first child
sibling — reference to the first sibling
return — reference to the parent

我很幸运地在这里找到了Sebastian Markbåge概述的算法要点。为了实现这个算法，我们需要一个包含3个字段的数据结构。

子女 - 第一个子女的引用
兄弟姐妹--指第一个兄弟姐妹
return--指向母体的引用

In the context of the new reconciliation algorithm in React, the data structure with these fields is called Fiber. Under the hood it’s the representation of a React Element that keeps a queue of work to do. More on that in my next articles.

在React新的调和算法中，带有这些字段的数据结构叫做Fiber。在外壳下，它是一个React Element的表示，它保留了一个工作队列。关于这一点，我在接下来的文章中会有更多的介绍。

The following diagram demonstrates the hierarchy of objects linked through the linked list and the types of connections between them:

下图展示了通过链接列表链接的对象的层次结构以及它们之间的连接类型。

So let’s first define our custom node constructor:

所以我们先定义一下我们的自定义节点构造函数。

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

And the function that takes an array of nodes and links them together. We’re going to use it to link children returned by the render method:

以及接受一个节点数组并将它们链接在一起的函数。我们要用它来链接渲染方法返回的子节点。

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

The function iterates over the array of nodes starting from the last one and links them together in a singly linked list. It returns the reference to the first sibling in the list. Here is a simple demo of how it works:

该函数从最后一个节点开始遍历节点数组，并将它们链接到一个单独的链接列表中。它返回对列表中第一个兄弟姐妹的引用。下面是一个简单的工作演示。

```javascript
const children = [{name: 'b1'}, {name: 'b2'}];
const parent = new Node({name: 'a1'});
const child = link(parent, children);

// the following two statements are true
console.log(child.instance.name === 'b1');
console.log(child.sibling.instance === children[1]);
```

We’ll also implement a helper function that performs some work for a node. In our case, it’s going to log the name of a component. But besides that it also retrieves the children of a component and links them together:

我们还将实现一个帮助函数，为节点执行一些工作。在我们的例子中，它将记录一个组件的名称。但除此之外，它还会检索一个组件的子节点，并将它们链接在一起。

```javascript
function doWork(node) {
    console.log(node.instance.name);
    const children = node.instance.render();
    return link(node, children);
}
```

Okay, now we’re ready to implement the main traversal algorithm. It’s a parent first, depth-first implementation. Here is the code with useful comments:

好了，现在我们准备好实现主要的遍历算法了。这是一个父先，深度优先的实现。下面是带有有用注释的代码。


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

Although the implementation is not particularly difficult to understand, you may need to play with it a little to grok it. Do it here. The idea is that we keep the reference to the current node and re-assign it while descending the tree until we hit the end of the branch. Then we use the return pointer to return to the common parent.

虽然这个实现并不是特别难理解，但你可能需要玩一玩才能摸清它。在这里做。这个想法是，我们保留对当前节点的引用，并在树的下降过程中重新分配它，直到我们到达分支的末端。然后我们使用返回指针返回到公共父节点。

If we now check the call stack with this implementation, here’s what we’re going to see:

如果我们现在用这个实现来检查调用栈，我们会看到以下内容。

As you can see, the stack doesn’t grow as we walk down the tree. But if now put the debugger into the doWork function and log node names, we’re going to see the following:

正如你所看到的，当我们向下走的时候，堆栈并没有增长。但如果现在把调试器放到doWork函数中，并记录节点名称，我们就会看到以下内容。

It looks like a callstack in a browser. So with this algorithm, we’re effectively replacing the browser’s implementation of the call stack with our own implementation. That’s what Andrew describes here:

它看起来就像浏览器中的调用栈。所以，通过这种算法，我们有效地用自己的实现取代了浏览器对调用栈的实现。这就是Andrew在这里所描述的。

Fiber is re-implementation of the stack, specialized for React components. You can think of a single fiber as a virtual stack frame.

光纤是栈的再实现，专门针对React组件。你可以把单个光纤看作是一个虚拟的栈框架。

Since we’re now controlling the stack by keeping the reference to the node that acts as a top frame:

由于我们现在通过保持对作为顶层框架的节点的引用来控制栈。

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

we can stop the traversal at any time and resume to it later. That’s exactly the condition we wanted to achieve to be able to use the new requestIdleCallback API.

我们可以在任何时候停止遍历，并在稍后恢复到它。这正是我们想要达到的条件，以便能够使用新的 requestIdleCallback API。

Work loop in React
React中的工作循环

Here’s the code that implements work loop in React:
这是React中实现工作循环的代码。


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

As you can see, it maps nicely to the algorithm I presented above. It keeps the reference to the current fiber node in the nextUnitOfWork variable that acts as a top frame.

正如你所看到的，它很好地映射到我上面介绍的算法。它将当前光纤节点的引用保留在作为顶格的nextUnitOfWork变量中。

The algorithm can walk the components tree synchronously and perform the work for each fiber node in the tree (nextUnitOfWork). This is usually the case for so-called interactive updates caused by UI events (click, input etc). Or it can walk the components tree asynchronously checking if there’s time left after performing work for a Fiber node. The function shouldYield returns the result based on deadlineDidExpire and deadline variables that are constantly updated as React performs work for a fiber node.

该算法可以同步行走组件树，并为树上的每个纤维节点执行工作（nextUnitOfWork）。这通常是UI事件（点击、输入等）引起的所谓交互式更新的情况。或者它也可以异步走动组件树，检查在为一个fiber节点执行工作后是否还有时间。函数shouldYield根据deadlineDidExpire和deadline变量返回结果，这些变量在React为光纤节点执行工作时不断更新。

The peformUnitOfWork function is described in depth here.

peformUnitOfWork函数在这里有深入的介绍。