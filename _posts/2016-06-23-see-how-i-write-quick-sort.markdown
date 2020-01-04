---
layout: post_with_octocat
title: 我尝试去写快排，结果。。。
date: 2016-06-23 20:56:50
excerpt: 为什么知道原理还是写不出正确的程序呢？
categories: tech
tags:
- algorithm
- quick sort
- ruby
---

《编程珠玑》第 32 页，提到：“尽管第一个二分查找程序于1946年就已经公布了，但是第一个没有 bug 的二分查找程序在 1962 年才出现。”还说参加课堂测试的专业程序员中， 90% 写的二分查找程序都有 bug 。

真的有那么难吗？我心血来潮，动手写起了快排（不要问为什么不是二分查找）。隐约记得快排的原理如下：

- 在要排序的元素集合中选定一个元素作比较标杆；其他元素分别与此标杆比较，比它小的放在标杆前面，比它大的放在它后面；
- 这样集合就一分为二，对这两部分分别应用步骤一的方法，直到每部分只有一个元素。

简单地写几个测试用例。结果第二个测试就跑不过。**为什么知道原理还是写不出正确的程序呢？**

聪明的人很快就能调试好出错的程序；记忆力好的，大概见过一次正确的写法后就不会忘。可惜普通人这两样都不占。

那如果普通人的目标是以后能很快地写出快排，应该怎样做呢？我暂时能想到：

- 在原理之上唤醒更多写快排的基本算法思想：一分为二用到分治法；算法会反复用到步骤一，所以有递归；算法不需要额外空间。

- 用少量的待排序元素辅助书写算法。

- 用测试用例保证算法正确性。

根据这个思路，首先要定义使用快排程序的方法：

    #!/usr/bin/env ruby
    sorted_array = QS.sort(array)

然后定义程序的大致框架：

    #!/usr/bin/env ruby

    module QS
      extend self
      def sort array
        inner_sort array, 0, array.size - 1
        array
      end
      def inner_sort array, low_pos, hight_pos
      end
      def divide array, low_pos, hight_pos
      end
      def exchange array, i, j
      end

    end

inner_sort 跟 divide 为什么要接受两个位置参数？我们没有额外储存空间可用，所以要用上下边界划定排序的作用范围。inner_sort 没有返回值，而 divide 要返回一个位置，确立递归排序的界限。exchange 用来交换元素。

开始写 inner_sort ：

    #!/usr/bin/env ruby

    module QS
      ...

      def inner_sort array, low_pos, hight_pos
        return if low_pos >= hight_pos
        division = divide array, low_pos, hight_pos
        inner_sort array, low_pos, division - 1
        inner_sort array, division + 1, hight_pos
      end

      ...

    end
    
程序会递归调用 inner_sort 。写递归要注意两点：

- 递归要有终止条件
- 每次递归都要朝着终止条件迈一步

接下来写 divide ：

    #!/usr/bin/env ruby

    module QS
      ...

      def divide array, low_pos, hight_pos
        target = array[low_pos]
        lo = low_pos
        hi = hight_pos
        while low_pos < hight_pos
          while array[low_pos] <= target && low_pos < hi
            low_pos += 1
          end
          while array[hight_pos] >= target && hight_pos > lo
            hight_pos -= 1
          end
          exchange(array low_pos, hight_pos) if low_pos < hight_pos
        end
        exchange(array, lo, hight_pos)
        hight_pos
      end

      ...

    end

divide 方法是快排中最难写、最容易出错的，为免出错：

- 要记住重排元素的技巧
    从待排序集合的头部开始找到一个比标杆元素大的，从尾部开始找到一个比标杆元素小的，然后交换两者位置
- 要正确写出比较、查找的上下界限
    在遍历元素时要注意数组越界问题和交换元素位置的附加条件： low_pos 必须小于 hight_pos
- 最后要把标杆元素与某个元素交换位置
    把标杆元素摆到中间，至于是通过跟 low_pos 还是跟 hight_pos 交换达到这个目的。可以用简单的例子（这个例子是尝试出来的，记不住也没关系）确定，假设待排序的元素集是 `[2,1,3]`，很容易就能得到要跟 hight_pos 交换。

把 exchange 方法补充好，测试用例也写上，完整的程序是这样的：

    #!/usr/bin/env ruby
    # usage QS.sort(array) => sorted array

    module QS
      extend self
      
      def sort array
        inner_sort array, 0, array.size - 1
        array
      end

      def inner_sort array, low_pos, hight_pos
        return if low_pos >= hight_pos
        division = divide array, low_pos, hight_pos
        inner_sort array, low_pos, division - 1
        inner_sort array, division + 1, hight_pos
      end
      
      def divide array, low_pos, hight_pos
        target = array[low_pos]
        lo = low_pos
        hi = hight_pos
        while low_pos < hight_pos
          while array[low_pos] <= target && low_pos < hi
            low_pos += 1
          end
          while array[hight_pos] >= target && hight_pos > lo
            hight_pos -= 1
          end
          exchange(array low_pos, hight_pos) if low_pos < hight_pos
        end
        exchange(array, lo, hight_pos)
        hight_pos
      end
      
      def exchange array, i, j
        array[i], array[j] = array[j], array[i]
      end

    end

    if __FILE__ == $0
      require 'test/unit'
      class TestQS < Test::Unit::TestCase
        def test_0
          array = []
          expected = []
          assert_equal expected, QS.sort(array)
        end
        def test_1
          array = [1]
          expected = [1]
          assert_equal expected, QS.sort(array)
        end
        def test_2_0
          array = [1,2]
          expected = [1,2]
          assert_equal expected, QS.sort(array)
        end
        def test_2_1
          array = [2,1]
          expected = [1,2]
          assert_equal expected, QS.sort(array)
        end
        def test_2_2
          array = [1,1]
          expected = [1,1]
          assert_equal expected, QS.sort(array)
        end
        def test_3_0
          array = [1,2,3]
          expected = [1,2,3]
          assert_equal expected, QS.sort(array)
        end
        def test_3_1
          array = [1,3,2]
          expected = [1,2,3]
          assert_equal expected, QS.sort(array)
        end
        def test_3_2
          array = [3,2,1]
          expected = [1,2,3]
          assert_equal expected, QS.sort(array)
        end
        def test_3_3
          array = [2,1,3]
          expected = [1,2,3]
          assert_equal expected, QS.sort(array)
        end
        def test_3_4
          array = [1,1,2]
          expected = [1,1,2]
          assert_equal expected, QS.sort(array)
        end
        def test_3_5
          array = [1,1,1]
          expected = [1,1,1]
          assert_equal expected, QS.sort(array)
        end
        def test_3_6
          array = [1,2,1]
          expected = [1,1,2]
          assert_equal expected, QS.sort(array)
        end
        def test_3_7
          array = [2,1,1]
          expected = [1,1,2]
          assert_equal expected, QS.sort(array)
        end
      end
    end