---
layout: post
title: react hooks and closure
date: 2020-05-26 10:20:28
excerpt: The root of all your troubles is that you don't know why.
lang: en
categories: 
- frontend
---

I recently took over a project written in react hooks. I've found that if someone has been around react hooks long enough, he/she will encounter the following problems：

- A state never updates
- A method is constantly executing

I'm not saying you won't run into the above problems with the Class Component. But when you compare the number of problems caused by these two approaches, and the difficulty of solving them, you'll find that react hooks has more problems and is more difficult to solve.

I can write a lot if I want to, but this article is more about why there are so many problems while using react hooks.

The first thing to say is. `The function component will be executed from top to bottom every time it is rendered.` It's so self-evident that the official documentation doesn't even mention it.

This concept is very important. With this concept in mind, you'll be interested in the implementation of `useState`. It's a method that passes the same arguments each time, but returns different results. 

And you'll have a much better understanding of the problem ['Why am I seeing stale props or state inside my function?'][1] than the official documentation.

The following code is from the official documentation.

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

The `Example` function component will be executed from top to bottom due to the rendering process triggered by `setCount`. The `handleAlertClick` method is thus redefined once again.

If you know anything about closures, this `handleAlertClick` is a closure, and the `count` it references internally is also a closure.

You click `Show alert` after the function component is executed (rendered). The value of `count` displayed when `alert` is executed 3 seconds later is the value at the moment you clicked `Show alert`.

`useEffects` is not that different from the normal functions or variables within function components.

Each time a function component is rendered, the `useEffects` inside will be executed from top to bottom, but it depends whether the `side effect` as its first argument will be executed after rendering.

As long as these `side effects` are executed, they are executed as closures. This means that both `state` and `props`, which are internally referenced in `side effect`, will remain as they were when the function component was last rendered.

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

In the above code, no matter how fast you click `Click me`, `console.log` will print out `count` one by one, starting at 0.

This behavior has nothing to do with asynchronous execution, look at the following [example][2] without `setTimeout`.

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

All `onClick` events are registered only at `componentDidMount`, are not updated after that, and point to `increaseCount` at that time. So no matter how many times you click `try clike me`, `count` is always 1, and the console always prints 0.

As a warm up, it's easy to spot the problem with the above few examples. Take a look at the following.

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

The noteworthy thing about the above code is that the `runner` method passes itself into `bar`, where it is executed as a callback.

Run it [here][3] and you'll see that the console keeps printing the value of `loading`, but it's always `false`, which is inconsistent with what's shown on the page.

Obviously, the re-rendering is triggered by `setLoading(true)`, but why is the value of `loading` in the console always `false`?

The reason for this is that the second and subsequent calls of `runner` are in the form of `callback`.

This `callback` points to the `runner` that comes after the initial rendering, the `foo` it contains, and the `loading` of `foo` all maintain their initial rendering values.

Since the value of `loading` is `false` after the initial rendering, the console's `loading` is always `false`.

Incidentally, if you remove the second parameter `[]` from `useEffect` above, you will see that the console prints out two values of `loading` every 5 seconds, which are `false` and `true` respectively.

As smart as you are, you'll be able to figure out why, and I won't reveal the answer.


**Reference**

- [Why am I seeing stale props or state inside my function?][1]
- [A Complete Guide to useEffect](https://overreacted.io/a-complete-guide-to-useeffect/)


[1]:https://reactjs.org/docs/hooks-faq.html#why-am-i-seeing-stale-props-or-state-inside-my-function
[2]:https://codesandbox.io/s/affectionate-mountain-uh4k6?file=/src/App.js:76-656
[3]:https://codesandbox.io/s/gifted-matsumoto-56jxw?file=/src/App.js:485-578