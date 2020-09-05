---
layout: post
title: Excel can help you when reading the source code
date: 2020-09-05 10:20:28
excerpt: Didn't think so, did you? 
lang: en
categories: 
- tech
---

A while ago I had to prepare for a sharing within the front-end group, so I went to read the [mobx][1] source code.

As a full-fledged state management tool, the source code execution process for mobx is so long that I often look back at the stack information and find myself a dozen stacks away from where I started.

While mobx is very well named and the code structure is clear, the code execution flow is a bit long.

Whenever I can't remember the execution context of a piece of code, I always want to be able to keep track of the flow of code execution while I'm looking at the code.

Previously, I thought I could only use flowcharts to document code execution, but drawing flowcharts was a pain, with more than half the time spent drawing and adjusting styles.

I couldn't concentrate on reading the source code at all, so I never got around to drawing the flowcharts.

I just saw someone on Twitter saying that "The biggest competitor of many ToB products is actually Excel". I suddenly had an idea, could I use it to record code execution?

With some practice, I found that Excel really does work.

First, let's talk about my own needs, when reading the source code I focus on roughly only three.

- What are the sequential methods of implementation at the same level?
- Which Method Called by Which Method
- Which method is a bit special and needs a note on it

I therefore record the code execution as follows,

- Records the executing method in the order of "Row". If there is content above a cell, the program executes the content above the cell before executing the content of that cell.
- Records the method being called in the order of "Column".If there is content to the left of a Cell, that Cell is called from the left side.
- Rows have higher priority than columns; if there is content above and to the left of a cell, ignore the content to the left.
- Add empty cells to resolve conflicts between rows and columns when necessary.
- Comment additional information on the Cells.

As an example, look at the following code,

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

It could be recorded in the manner above as follows.

![Excel record]({{ site.url }}/assets/excel_record.jpg)*Excel record*

There must be logical judgments in the code, how to handle logical branches? Here's what I've come up with for now.

- Record different branches with different columns
- Every branch having the same background color
- Insert one empty column between each branch
 
For example,

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

Record the above code in Excel like this,

![Excel record with condition]({{ site.url }}/assets/excel_record_condition.jpeg)*Excel record with condition*

Useing Excel to record the code execution although rudimentary, not as intuitive as a flowchart, but very hassle-free, and easy to read, I am very satisfied.

[1]:https://mobx.js.org