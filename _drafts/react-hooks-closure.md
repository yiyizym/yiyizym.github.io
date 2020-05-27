---
layout: post
title: react hooks 与闭包
date: 2020-05-26 10:20:28
excerpt: 所有烦恼的根源就在于你不知道为什么
categories: 
- frontend
---

最近接手一个用 react hooks 写的项目，与所有接触过 react hooks 的人一样，只要时间够长，就一定会遇到以下问题：

- 某个 state 一直不会更新
- 某个方法疯狂执行

我不是说用传统的方法就不会遇到上面的问题。但是仔细比较两种写法引发问题的次数，以及解决问题的难度之后，你就会发觉 react hooks 问题更多更难解决。

要继续吐槽的话，可以写很多。但这篇文章更想写为什么用上 react hooks 后会有这么多问题，问题的根源是什么。

首先要说的是，`函数式组件在每次 render 时，会从上到下执行一遍`。这像是不言而喻的事情，以至于官方文档根本没有提及。

但这个概念非常重要，要是记住了，你就会对 `useState` 的实现很感兴趣，它是个每次传入相同的参数，但会返回不同结果的方法。

要是记住了，你就会对这个问题：[Why am I seeing stale props or state inside my function?](https://reactjs.org/docs/hooks-faq.html#why-am-i-seeing-stale-props-or-state-inside-my-function)有比官方文档更深刻的理解。

把描述问题的代码搬下来：

```javascript
function Example() {
  const [count, setCount] = useState(0);

  function handleAlertClick() {
    setTimeout(() => {
      alert('You clicked on: ' + count);
    }, 3000);
  }

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
      <button onClick={handleAlertClick}>
        Show alert
      </button>
    </div>
  );
}
```

`Example` 函数组件会因为由 `setCount` 而触发的 render 过程，从上到下执行一遍。

`handleAlertClick` 方法也会因此被重新定义一遍，如果你对闭包有了解，这个 `handleAlertClick` 就是闭包，它内部引用的 `count` 也是闭包。

因为闭包，你得以

`alert` 执行时显示的 `count` 值，是你点击 `Show alert` 那一刻的值，也是距离你点击 `Show alert` 最近的一次 `render` 之后的值。



## Effects always “see” props and state from the render they were defined in. 

## 叠加上闭包

