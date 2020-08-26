---
layout: post
title: CSS animation 多动画
date: 2018-05-20 04:36:27
excerpt: 这是篇水文
categories: frontend
---

**序**

这是篇笔记性质的文章，没多少技术含量。

之前一直很少接触 CSS 动画，前段时间刚好做了个相关活动，实现了包含位移、渐现、一次性效果和循环效果的动画。

**效果**

可以在[这里](http://judes.me/ballon_animation_demo)先看一下最终效果。

**关键代码**

完整代码在[这里](https://github.com/yiyizym/ballon_animation_demo)。

[原理](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations/Using_CSS_animations#Setting_multiple_animation_property_values)是在 animation 对应属性下设置多个值，下面摘取关键的代码：

```css
.ballon {
  animation-name: ballon_moveup, ballon_show, ballon_floating;
  animation-duration: 1s, 0.8s, 5s;
  animation-delay: 1s, 1.2s, 2s;
  animation-iteration-count: 1, 1, infinite;
  animation-fill-mode: forwards, forwards, forwards;
  animation-timing-function: cubic-bezier(0.40, 0.00, 0.20, 1.00), cubic-bezier(0.33, 0.00, 0.67, 1.00), cubic-bezier(0.40, 0.00, 0.20, 1.00), cubic-bezier(0.33, 0.00, 0.67, 1.00);
}
@keyframes ballon_moveup {
  from {
    transform: translate3d(0, 166.6px, 0);
  }
  to {
    transform: translate3d(0, 0, 0);
  }
}
@keyframes ballon_show {
  to {
    opacity: 1;
  }
}
@keyframes ballon_floating {
  0% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, 27px, 0);
  }
  100% {
    transform: translate3d(0, 0, 0);
  }
}
```

用 `animation-iteration-count` 设置动画循环次数，实现一次性动画和循环动画；

用 `animation-fill-mode` 设置当动画结束后，元素应用的是动画第一帧(backwards)、最后一帧(forwards)的样式，还是都不用(none)、都用(both)；

在 `animation-timing-function` 中，如果设置了比动画数量要少的函数，那么会从头开始循环使用函数，比如有 4 个动画，但只有 3 个函数，第 4 个动画会使用第 1 个函数。 反过来，如果函数比动画多，多出来的函数会被截断不用。

**参考**

- [Using CSS animations](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations/Using_CSS_animations#Setting_multiple_animation_property_values) 

- [transition-timing-function](https://developer.mozilla.org/en-US/docs/Web/CSS/transition-timing-function) 