---
layout: post
title: 怎样抑制在父组件调用子组件方法的冲动？
date: 2019-06-02 10:20:28
excerpt: 或许你在用 React 时也会遇到同样的问题
lang: zh_CN
categories: 
- frontend
---

最近都在写 React ，官网有很多应对各种情境的最佳实践指引。

不过有时候你总会遇到使用既有接口解决不了、并且没有最佳实践的问题。

比如我遇到这样的：

如果你只有一个表单，提交表单的整个流程就是：填写、校验、提交、重置；

如果你在一个页面有多个表单，提交它们的整个流程就是：填写各自的表单、各自校验、整体提交、各自重置。

如果把提交的逻辑放到父组件上，让各个表单作为子组件，那么校验、重置这些都是子组件的方法，在用户点击提交时才做校验、在提交成功后重置表单，就变成了在父组件上调用子组件的方法了。

你可能有疑问：为什么要在一个页面里面放多个表单，把它们都整合成一个不就没那么多事情了吗？

如今想想，要是在开头就预见往后会遇到这么麻烦的事情，或许会考虑把它们放在一个表单，但这样一来整个表单会有 25 个字段，8 种不同的表单子组件，代码量会有多大啊！

还是算了，遇到问题别想着后退，想着怎样解决才是王道。不就是“在父组件里调用子组件的方法”吗？直觉告诉我，这种需求应该早就有不少人提出来过，搜索一下应该会有相关讨论。

不久，我就总结出三种做法：

1. 通过 ref api ，父组件获取子组件的引用，然后由父组件在适当的时候调用子组件的方法。具体做法看[这里](https://reactjs.org/docs/refs-and-the-dom.html#adding-a-ref-to-a-class-component)。

这种方式的好处就是，嗯，除了能达成「在父组件中调用子组件的方法」这个目标之外，想不出其他的好处了。

它的限制是，子组件必须是 `class component` ，不能是 `function component` ，因为 ref 引用的是组件实例，而 `function component` 没有实例。

它的坏处是，破坏了子组件的封装：把子组件自身的方法暴露到外面、被直接调用，使以后修改子组件变得困难。

2. 父组件向子组件传递一个事件发布订阅器，让子组件自行注册/注销方法，父组件负责发布事件。简单代码如下：

```
// PubSub.js
const events = new Set();

export default {
  pub() {
    events.forEach(fn => fn());
  },
  sub(callback) {
    events.add(callback);
    return () => events.delete(callback);
  }
}

// Child.js
class Child extends React.Component {
  componentDidMount() {
    this.unlisten = pubsub.sub(() => this.setState({ ... }));
  }

  componentWillUnmount() {
    this.unlisten();
  }

  render() { ... }
}

// Parent.js
class Parent extends React.Component {
  render() {
    return <div><Child /><button onClick={pubsub.pub} /></div>;
  }
}
```

这种方式代码会多一点，好处是父子组件解耦：父组件不用知道子组件的具体实现、子组件没有暴露自己的方法。

3. 父组件向子组件传递一个标志属性，子组件监听这个属性的变化，当它有变化时调用自己的方法。

这种方式实现起来比较简单，适用于处理简单的问题，如 table 子组件重新请求数据刷新自身，或者表单子组件重置所有字段等等；但面临复杂的情况，如子组件调用自身方法时可能会（同步或异步）触发更新父组件状态（父组件很难确定自身状态是否已经更新完成），还是第二种方式比较好。

