---
layout: post
title: 阅读源码时 excel 能帮到你
date: 2020-08-28 10:20:28
excerpt: 没想到吧？读源码能有 excel 什么事？
lang: zh_CN
categories: 
- tech
---

前段时间要准备组内分享，跑去读 mobx 的源码。

作为一个成熟的状态管理库， mobx 的源码执行流程非常长，以致我经常在回看信息时发现自己离最初的位置有十几层堆栈了。

虽然 mobx 的命名非常好，代码结构也清晰，但流程实在有点长，每当我记不住某段代码的前后流程时，总希望能一边看代码，一边记录下代码执行的流程。

之前我以为只能用流程图记录代码执行，但是画流程图很麻烦，超过一半时间都在画画、调整样式。这样完全没心思读源码了。

刚好那阵子刷推，看到有人说「很多 ToB 产品做到最后发现最大的竞争对手其实是 Excel」，我想 Excel 这么强大，能不能用它来记录代码执行呢？

经过一系列实践，我发现 Excel 真的可以。

说说自己的需求，读源码时我关注点大体只有三个：

- 处在同一层级、按顺序执行的方法有哪些
- 哪个方法调用了哪个方法
- 哪个方法有点特别，需要备注一下

因此我按下面的方式用 Excel 记录代码执行：

- 按「行」记录先后执行的方法，如果某个「单元格」上方有内容，表明程序先执行了上方的内容，再执行本单元格内容
- 按「列」记录被调用的方法，如果某个「单元格」左侧有内容，表明本单元格被左侧调用
- 「行」的优先级比「列」的高；如果某个「单元格」上方、左侧都有内容，忽略左侧内容
- 在必要时加入空「单元格」解决「行」跟「列」的冲突
- 在「单元格」上评论额外信息


举个例子，看下面的代码：

```javascript
function func1 () {
  funcA();
  funcB();
  funcC();
}

function funcA() {
  funcAA();
  funcAB();
  funcAC();
}

function funcB() {
  funcBA();
  funcBB();
  funcBC();
}
```

按上面的方式可以记录成这样：

![excel record]({{ site.url }}/assets/excel_record.jpg)*excel record*

代码少不了逻辑判断，怎样处理逻辑分支呢？我暂时想到的办法是

- 用不同的列记录不同的分支
- 每个分支用相同背景色标注
- 不同分支间隔一列
 
举例说明：

```javascript
function func1 () {
  funcA();
  funcB();
}

function funcA() {
  funcAA();
  funcAB();
  funcAC();
}

function funcB() {
  if(Math.random() > 0.5) {
    funcBA();
  } else {
    funcBB();
  }
}

```

用 Excel 这样记录以上代码：

![excel record with condition]({{ site.url }}/assets/excel_record_condition.jpeg)*excel record with condition*

用 Excel 记录代码执行虽然简陋了点，也没有流程图直观，但非常的快，也方便搜索，我非常满意。