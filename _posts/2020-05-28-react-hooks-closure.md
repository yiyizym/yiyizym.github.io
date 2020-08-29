---
layout: post
title: react hooks 与闭包
date: 2020-05-26 10:20:28
excerpt: 所有烦恼的根源就在于你不知道为什么
lang: zh_CN
categories: 
- frontend
---

最近接手一个用 react hooks 写的项目。我发现只要接触 react hooks 的时间够长，就一定会遇到以下问题：

- 某个 state 一直不会更新
- 某个方法疯狂执行

我不是说用传统方法就不会遇到上面的问题。但是仔细比较两种写法引发问题的次数，以及解决问题的难度之后，你就会发觉 react hooks 问题更多更难解决。

要继续吐槽的话，可以写很多。但这篇文章更想写为什么用上 react hooks 后会有这么多问题，问题的根源是什么。

首先要说，`函数式组件在每次渲染时，会从上到下执行一遍`。这像是不言而喻的事情，以至于官方文档根本没有提及。

但这个概念非常重要，要是记住了，你就会对 `useState` 的实现很感兴趣，它是个每次传入相同的参数，但会返回不同结果的方法。

要是记住了，你就会对这个问题：[Why am I seeing stale props or state inside my function?][1]有比官方文档更深刻的理解。

把官方文档代码搬下来：

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

`Example` 函数组件会因为由 `setCount` 而触发的渲染过程，从上到下执行一遍。

`handleAlertClick` 方法也会因此被重新定义一遍，如果你对闭包有了解，这个 `handleAlertClick` 就是闭包，它内部引用的 `count` 也是闭包。

因为闭包，你得以在函数组件执行(渲染)完后点击 `Show alert` 的触发 `handleAlertClick` ，因此 3 秒后 `alert` 执行时显示的 `count` 值，是你点击 `Show alert` 那一刻的值，也就不奇怪了。

`useEffects` 与函数组件内的普通函数、变量并没有多大不同。

每次渲染，函数组件内部的 `useEffects` 会从上到下执行一遍，只是作为它的第一个参数的 `side effect` 会不会在渲染结束后执行就得看情况。但是只要这些 `side effect` 执行，它们就是以闭包的姿态执行。这意味着 `side effect` 内部引用到的 `state` 跟 `props` 都会是函数组件最近一次渲染时的值。

```javascript
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setTimeout(() => {
      console.log(`You clicked ${count} times`);
    }, 3000);
  });

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

上面的代码，无论你点 `Click me` 有多快， `console.log` 都会将 `count` 从 0 开始逐个打印出来。

这个表现跟异步执行没什么关系，看看下面这个没有 `setTimeout` 的[例子][2]：

```javascript
export default function App() {
  const [count, setCount] = useState(0);
  const [list, setList] = useState([]);

  const increaseCount = () => {
    const newCount = count;
    console.log(newCount);
    setCount(newCount + 1);
  };

  useEffect(() => {
    const list = new Array(5).fill().map((_, index) => {
      return (
        <div key={index} onClick={increaseCount}>
          try click me
        </div>
      );
    });
    setList(list);
  }, []);

  return (
    <div className="App">
      <div className="list">{list}</div>
      <h2>{count}</h2>
    </div>
  );
}
```

所有的 `onClick` 事件都只在 `componentDidMount` 时注册，之后不再更新，并且都指向那时的 `increaseCount` 。因此无论你点了多少遍 `try clike me` ，`count` 都是 1 ，而控制台永远打印 0 。


上述几个例子作为铺垫，比较容易看出问题。来看看下面这个：

```javascript
export default function App() {
  const [loading, setLoading] = useState(false);

  const foo = () => {
    console.log("is loading ? ", loading);
  };

  const bar = callback => {
    setTimeout(() => {
      setLoading(true);
      callback();
    }, 5000);
  };

  const runner = () => {
    foo();
    bar(runner);
  };

  useEffect(() => {
    console.log("run");
    runner();
  }, []);

  return (
    <div className="App">
      <h1>Is it loading ?  {loading ? 'true' : 'false'}</h1>
    </div>
  );
}
```

上面代码值得注意的地方在于 `runner` 方法内部：会将自身传进 `bar` ，在其内作为回调被执行。

在[这里][3]运行一下，你会发现控制台不断打印 `loading` 的值，但这个值永远都是 `false` ，这与页面上显示的不一致。


明明是因为 `setLoading(true)` 才触发重新渲染，为什么控制台的 `loading` 却一直是 `false` 呢？

原因就在于 `runner` 在第二次及之后的调用都是以 `callback` 的形式。这个 `callback` 是一个指向初次渲染之后的 `runner` 。初始 `runner` 包含的 `foo` ，以及 `foo` 包含的 `loading` 都是初次渲染时的值。

初次渲染时 `loading` 的值是 `false` ，因此控制台的 `loading` 一直是 `false` 。

随带一提，如果你把上面的 `useEffect` 中第二个参数 `[]` 去掉，就会在控制台看到每隔 5 秒先后打印出 `loading` 的两个值，分别为 `false` 跟 `true` 。

以你的聪明才智，一定能弄明白为什么，我就此打住了。


**参考**

- [Why am I seeing stale props or state inside my function?][1]
- [A Complete Guide to useEffect](https://overreacted.io/a-complete-guide-to-useeffect/)


[1]:https://reactjs.org/docs/hooks-faq.html#why-am-i-seeing-stale-props-or-state-inside-my-function
[2]:https://codesandbox.io/s/affectionate-mountain-uh4k6?file=/src/App.js:76-656
[3]:https://codesandbox.io/s/gifted-matsumoto-56jxw?file=/src/App.js:485-578