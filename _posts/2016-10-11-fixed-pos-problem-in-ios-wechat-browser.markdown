---
layout: post
title: iOS浏览器内核导致 fixed 定位元素可能错位问题
date: 2016-10-11 21:32:43
description: 又是一个在开发微信企业号时遇到的问题，这次锅不在腾讯
categories: frontend
tags:
- 浏览器
- wechat
---

在企业号某个列表页面使用 `position: fixed;` 置顶搜索输入框时，发现一个诡异的问题：在 iOS 的微信浏览器中点击输入框，弹出输入法时，很有可能会（复现条件：列表长度超过一屏，在点击输入框前往下拖动列表）导致输入框错位下移，在 Android 微信浏览器中却没有问题。

![在 iOS 输入法未弹出时显示正常 ]({{ site.url }}/assets/problem_1.jpg)*在 iOS 输入法未弹出时显示正常*
![在 iOS 输入法弹出后出现错位 ]({{ site.url }}/assets/problem_2.jpg)*在 iOS 输入法弹出后出现错位*

出问题的页面结构大致如下，完整的代码见[这里](https://gist.github.com/zymiboxpay/1e0a620284d1cf320f5f9603779a728d)：

    <div class="container">
      <div class="fixed_part">
        <input type="text" placeholder="输入文字">
      </div>
      <div class="overflow_part">
        <!--items-->
      </div>
    </div>

相应的样式如下：

    .container {
      position: relative;
    }
    .fixed_part {
      position: fixed;
      top: 0;
      width: 100%;
    }
    .fixed_part > input {
      width: 100%;
      padding: 5%;
      border: none;
      border-bottom: 1px solid #eee;
    }
    .overflow_part .item {
      height: 100px;
      line-height: 100px;
      text-align: center;
      border-bottom: 1px solid #eee;
    }

最初遇到这个问题时，当作没看见（一，这是兼容性问题，手尾长；二，复现条件比较苛刻；三，产品经理没发现；四，手头上事情很多；五，不想做的理由总是很多），这事就过去了。

后来又再次遇到，一时兴起想解决它。很快找到原因（ iOS 原生浏览器内核对 fixed 定位元素渲染有 bug ），还看到有文章给出了[解决方案](http://efe.baidu.com/blog/mobile-fixed-layout/)。借鉴文中的思路——放弃使用 fixed 定位，同时缩窄滚动区域——给出了自己的解决方案，完整的代码见[这里](https://gist.github.com/zymiboxpay/de6885576848a072b776c51acc556737)。


页面结构没有改变。

样式有大改变：

    .container {
      /* 让容器计算出自身高度 */
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      /* 让子元素处理自身高度 */
      display: flex;
    }
    .fixed_part {
      /* 用 absolute 代替 fixed */
      position: absolute;
      top: 0;
      width: 100%;
    }
    .fixed_part > input {
      box-sizing: border-box;
      width: 100%;
      padding: 5%;
      border: none;
      border-bottom: 1px solid #eee;
    }
    .overflow_part {
      width: 100%;
      /* 让滚动条出现在高度超过一屏的元素上面 */
      overflow-y: auto;
    }
    .overflow_part .item {
      height: 100px;
      line-height: 100px;
      text-align: center;
      border-bottom: 1px solid #eee;
    }

这个方案的好处是不需要写死——你要这样做也是可以的——任何一个元素的高度。

完成后的效果图：

![在 iOS 输入法未弹出时显示正常 ]({{ site.url }}/assets/solution_1.jpg)*在 iOS 输入法未弹出时显示正常*
![在 iOS 输入法弹出后显示正常 ]({{ site.url }}/assets/solution_2.jpg)*在 iOS 输入法弹出后显示正常*