---
layout: post
title: 推导 Y 组合子
excerpt: "看不懂 the little schemer 第九章？请看这里"
date: 2014-10-18 16:47:38
keywords: scheme, Y-combinator, the little schemer
categories: tech
---
The Litter Schemer 的第九章，不读到最后，大概你都不知道作者其实是在一步步地推导Y组全子。

什么是Y组合子？答案在[这里](http://zh.wikipedia.org/zh-cn/%E4%B8%8D%E5%8A%A8%E7%82%B9%E7%BB%84%E5%90%88%E5%AD%90)。

看不懂？不要紧，记住Y组合子可以做什么就行了：**Y 组合子让我们可以定义匿名的递归函数**。

以下推导采用来自 The Little Schemer 的例子，并为每一步加上注解。

嘿喂狗！

假设我们要写一个求列表长度的 length 函数，很简单是不是？我们之前已经写过了：

	(define length
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					add1 (length (cdr list))))))

刚才我们定义了一个叫 length 的函数，现在假设我们不能给这个函数命名，只能使用匿名函数：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (??? (cdr list))))))

忽然间，我们没有办法递归调用上面这个匿名函数了。`???`是什么意思呢？原本这是函数名字，但匿名函数没有名字嘛～

现在我们唯一可以做的就是用 整个匿名函数 替换 `???`：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (

		(lambda (list)							; the
			(cond								;
				((null? list) 0)				; function
				(else							; 
					(add1 (??? (cdr list))))))	; itself

				 (cdr list))))))

虽然这是一个治标不治本的方法，因为`???`还藏在函数里面。但这个函数已经可以用来求长度为1或0的列表长度了。如果我们重复上一步：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (
			(lambda (list)							; the
				(cond								;
					((null? list) 0)				; function
					(else							;
						(add1 (??? (cdr list))))))	; itself
					 (cdr list))))))
				 (cdr list))))))

现在这个函数可以用来求长度为0,1,2的列表长度了，你可以这样一直替换下去，直到天荒地老。但这样会很累。而且函数里有大量重复的代码，这样很不好。

我们还是想想别的办法吧。首先，我们把引发重复代码的源头`???`从函数中提出来，把它当作函数的参数再传进去：

	((lambda (length)
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (length (cdr list)))))))
	???)

上面的代码首先调用了`lambda (length)`函数，并且把`???`当作参数传进去，最终返回了另一个匿名函数：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (??? (cdr list))))))

你没看错，这就是我们最初的那个匿名函数。现在我们用同样的方法——用整个匿名函数替换`???——重写一下可以求长度为0,1列表长度的匿名函数：

	((lambda (f)
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (f (cdr list)))))))
	 ((lambda (g)
		 (lambda (list)
			 (cond
				 ((null? list) 0)
				 (else
					 (add1 (g (cdr list)))))))
	???))

上面的代码首先把`???`传给`lambda(g)`函数，然后把返回的函数——就是最初的匿名函数——传给`lambda(f)`，最终得到：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (??? (cdr list))))))
				 (cdr list))))))

上面的代码是不是很眼熟？它就是之前那个可以求长度为0,1的列表长度的函数，运用同样的方法可以得到求长度为0,1,2的列表长度的函数：

	((lambda (f)
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (f (cdr list)))))))
	 ((lambda (g)
		 (lambda (list)
			 (cond
				 ((null? list) 0)
				 (else
					 (add1 (g (cdr list)))))))
	  ((lambda (h)
		  (lambda (list)
			  (cond
				  ((null? list) 0)
				  (else
					  (add1 (h (cdr list)))))))
	???)))

因为函数的参数名字叫什么都没关系，我们不妨把`f,g,h`改成更有意义的名字：`length`：

	((lambda (length)
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (length (cdr list)))))))
	 ((lambda (length)
		 (lambda (list)
			 (cond
				 ((null? list) 0)
				 (else
					 (add1 (length (cdr list)))))))
	  ((lambda (length)
		  (lambda (list)
			  (cond
				  ((null? list) 0)
				  (else
					  (add1 (length (cdr list)))))))
	???)))

到这步，我们又写了重复的代码。再一次，我们把重复的部分提出来，写一个`mk-length`函数帮我们生成`length`函数：

	((lambda (mk-length)
		(mk-length ???))
	 (lambda (length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 (length (cdr list))))))))

仔细观察上面的代码，`(lambda (mk-length) ...)`函数把`(lambda (length) ...)`函数当作`mk-length`参数传进去了。而`(lambda (length) ...)`函数则把`???`当作`length`参数，返回最初的匿名函数：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (??? (cdr list))))))

我们利用`mk-length`再次重写一下求长度为1的列表长度的函数，只需要对原`mk-length`函数的参数`???`再调用一次`mk-length`：

	((lambda (mk-length)
		(mk-length 
			(mk-length ???)))
	 (lambda (length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 (length (cdr list))))))))

分析上面的代码，首先我们把`(lambda (length) ...)`函数当作`mk-length`参数传进`(lambda (mk-length) ...)`函数。这样得到的函数将把`(mk-length ???)`返回的结果当成参数，还记得`(mk-length ???)`返回什么吧？没错，就是最初的那个匿名函数。上面的代码展开之后就成了可以求长度为0,1的列表长度的函数了：

	(lambda (list)
		(cond
			((null? list) 0)
			(else
				(add1 (
		(lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (??? (cdr list))))))
				 (cdr list))))))

类似地，可以写出求长度为0,1,2的列表长度的函数：

	((lambda (mk-length)
		(mk-length 
			(mk-length
				(mk-length ???))))
	 (lambda (length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 (length (cdr list))))))))

因为我们并不关心`???`到底是什么东西，不妨把它替换为`mk-length`：

	((lambda (mk-length)
		(mk-length mk-length))
	 (lambda (length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 (length (cdr list))))))))

上面这个函数与原版的不同之外就只是原来是`???`的地方，现在是：

	(lambda (length)
		 	(lambda (list)
		 		(cond
		 			((null? list) 0)
		 			(else
		 				(add1 (length (cdr list)))))))

但这不影响我们求长度为0的列表长度，因为根本用不着。让我们改一下函数的参数名字——之前我们做过类似的事情——把`length`改为`mk-length`：

	((lambda (mk-length)
		(mk-length mk-length))
	 (lambda (mk-length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 (mk-length (cdr list))))))))

接下来我们要做最关键也是最神奇的一步，把最后面一个`mk-length`用`(mk-length mk-length)`替换：

	((lambda (mk-length)
		(mk-length mk-length))
	 (lambda (mk-length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 ((mk-length mk-length) (cdr list))))))))

上面的代码可以计算任意长度列表的长度哦，不信你试试下面这个：

	(((lambda (mk-length)
		(mk-length mk-length))
	 (lambda (mk-length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 ((mk-length mk-length) (cdr list))))))))
	 '(a b c d e f g h i j))

如果上面的代码太复杂，不妨看看这个简化的例子：

	(lambda (m)
		(m m)
	 (lambda (l)
	 	(l l)))

上面的函数展开之后，还是得到自己！这样它就可以无限循环下去了。我们的`mk-length`函数也是类似的，只不过因为`list`长度会不断递减，所以函数最终会停下来。不过我们还没有得出Y组合子，我们还得把Y组合子与真正干活的那部分函数分离开来！

我们先来看看这个：`(mk-length mk-length)`，它以`(cdr list)`为参数，事实上，这与下面的函数等价：

	(lambda (x)
		((mk-length mk-length) x))


用上面的函数替换`(mk-length mk-length)`，得到：


	((lambda (mk-length)
		(mk-length mk-length))
	 (lambda (mk-length)
	 	(lambda (list)
	 		(cond
	 			((null? list) 0)
	 			(else
	 				(add1 (

	 					(lambda (x)
							((mk-length mk-length) x))

	 					(cdr list))))))))

然后我们故技重施，把`(lambda (x) ...)`提出来：

	((lambda (mk-length)
		(mk-length mk-length))
	 (lambda (mk-length)

	 	((lambda (length) 								;
	 		(lambda (list) 								;
	 			(cond									;
	 				((null? list) 0)					;
		 			(else 								;
		 				(add1 (length (cdr list)))))))	;

		(lambda (x)
			((mk-length mk-length) x)))))

来看看上面代码中间与其他代码隔开来的部分，这部分是真正”干活“的，我们把它提出来：

	((lambda (le)
		((lambda (mk-length)
			(mk-length mk-length))
		 (lambda (mk-length)
			(le (lambda (x)
					((mk-length mk-length) x))))))

 	(lambda (length) 								;
 		(lambda (list) 								;
 			(cond									;
 				((null? list) 0)					;
	 			(else 								;
	 				(add1 (length (cdr list))))))))	;

就这样，我们得到了两部分代码，上一部分就是Y组合子，把`mk-length`重命名为`f`：

	((lambda (le)
		((lambda (f)
			(f f))
		 (lambda (f)
			(le (lambda (x)
					((f f) x))))))

 	(lambda (length) 								;
 		(lambda (list) 								;
 			(cond									;
 				((null? list) 0)					;
	 			(else 								;
	 				(add1 (length (cdr list))))))))	;

为方便以后使用，还可以把上半部分的代码定义为 `Y` 函数：

	(define Y
		(lambda (le)
			((lambda (f) (f f))
				(lambda (f)
					(le (lambda (x) ((f f) x)))))))

最后，利用 `Y` 函数重写`length`函数：

	((Y (lambda (length)
		（lambda (list)
			(cond
				((null? list) 0)
				(else
					(add1 (length (cdr list)))))))
	'(a b c d e f g h i j))

**参考文献**

- 原文 [Deriving the Y-Combinator](http://www.catonmat.net/blog/derivation-of-ycombinator/)

- [理解Y Combinator](http://a-shi.org/blog/2014/10/05/li-jie-y-combinator/)