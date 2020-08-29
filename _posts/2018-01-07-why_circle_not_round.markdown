---
layout: post
title: 说好一起变圆，你怎么就瘦了？
date: 2018-01-07 02:47:23
excerpt: 浏览器画圆圈问题
lang: zh_CN
categories: frontend
---

### 序

前几天，同事让我看看一个问题。

他让几个圆并排成一直线，很简单的一件事情。


![排成一行的 7 个圆]({{ site.url }}/assets/circle_not_round_1.png)*排成一行的 7 个圆*

最后视觉验收不通过，因为这里面有几个圆变扁了。用工具量一下，确实如此：

![有的圆变扁了]({{ site.url }}/assets/circle_not_round_1_1.png)*有的圆变扁了*

我仔细看这一排 7 个圆，发现不是所有的圆都变扁了，变扁的只有两三个。从前端代码上看所有的圆都应用相同的样式：

![圆的样式相同]({{ site.url }}/assets/circle_not_round_2.png)*圆的样式相同*

从浏览器计算出来的数值上看所有的圆直径相同：

![圆的直径相同]({{ site.url }}/assets/circle_not_round_3.png)*圆的直径相同*

当我把圆的直径设为整数时，所有的圆都正常显示。

![直径为整数的圆]({{ site.url }}/assets/circle_not_round_1_2.png)*直径为整数的圆*


经过在网上一番调查与思考，我终于明白了原因。

### 为什么浏览器上显示的数值与渲染效果不一样？

原来根据[规范](https://www.w3.org/TR/css-cascade-3/#used)，浏览器在计算属性的值时，最终会得出一个叫做 `used value` 的“绝对理论值”。但浏览器在渲染时可能不能直接使用这个 `used value`，这时只能使用这个值的近似值，这个近似值叫做 `actual value` 。

Chrome 浏览器的调试工具中显示的所有数值，是 `used value` ，调用 `DOMelement.getBoundingClientRect()` 也能得到 `DOMelement` 的所有 `used value` 。而我们肉眼看到的尺寸是用 `actual value` 渲染出来的。

![用 getBoundingClientRect 得到 used value]({{ site.url }}/assets/circle_not_round_4.png)*用 getBoundingClientRect 得到 used value*

### 为什么小数会让圆变扁

因为浏览器只能渲染整数倍象素长度，我们的圆的直径是小数，所以只能用近似后的整数值。

### 但为什么有些圆看上去是正常的呢？

有些圆看上去正常，有些却变扁，要弄清楚这个现象，得先了解 `actual value` 的计算公式。

采用 webkit 内核的浏览器，`actual value` 的计算具体公式是这样的：

```
  定义几个变量：
  x : 圆在横轴上方向位置， used value
  y : 圆在纵轴上方向位置， used value
  width : 圆的宽， used value
  height : 圆的长， used value

  x' : 圆在横轴上方向的实际位置， actual value
  y' : 圆在纵轴上方向的实际位置， actual value
  width' : 圆的实际宽， actual value
  height' : 圆的实际长， actual value

  actual value 计算公式：

  x' = round(x)
  y' = round(y)

  width' = round(x + width) - round(x)
  height' = round(y + height) - round(y)

```

这些圆横着排成一排，所以它们的 y 和 height 都是一样的，计算后的 y' 和 height' 也一样，而因为 x 值都不一样，计算后的 width' 就有可能不一样，不过所有圆之间的 width' 最多相差 1 。

最终看到的效果就是，有几个圆是正常的（height' 跟 width' 值一样），而另外几个圆在相同的方向上（横轴或纵轴）变扁。圆的直径越小，变扁就越明显。

下图用公式计算第一个圆与第二个圆的直径，可以看到两者在横轴上相差 1 ：

![用公式计算 actual value]({{ site.url }}/assets/circle_not_round_5.png)*用公式计算 actual value*

### 有办法让圆的实际尺寸跟设计稿一致吗？

要让圆的实际尺寸跟设计稿一致，除了设置圆的直径（used value）为整数，没有别的办法。

注意，如果圆的直径以 em/rem/vw 等等为单位，经过计算后的以 px 作为单位的值就已经跟设计稿的值有差距。

因为各个浏览器在处理小数时保留多少位都有自己的实现，再经过乘法计算后，最终的值很难跟设计稿上的对得上。

如果圆的直径（used value）一定要是小数，只能做到尽量跟设计稿差距小一点。

如果适配 webkit 内核浏览器的话，建议把这个小数定为 1/64 的倍数。这个 `1/64` 是 webkit 内核浏览器的精度，浏览器会把值放大 64 倍、取整后保存下来，使用时取出来直接除以 64 ，保留小数。

为什么是 64 ？可能是左移 8 位（位运算）速度比较快吧。

## 参考资料

[浏览器将rem转成px时有精度误差怎么办？](https://www.zhihu.com/question/264372456/answer/280496269)

[rem 产生的小数像素问题](http://taobaofed.org/blog/2015/11/04/mobile-rem-problem/)

[actual value 计算公式， webkit 官方文档](http://trac.webkit.org/wiki/LayoutUnit)

[CSS 子元素依次收缩的实现，里面有提到浏览器的精度](http://lotabout.me/2017/flex-shrink-in-order/)