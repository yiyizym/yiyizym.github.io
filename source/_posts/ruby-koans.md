title: ruby_koans
date: 2015-08-23 10:18:33
description: some notes about ruby when practicing with ruby koans
categories: ruby
tags: 
- ruby
---



# about blocks

## methods can calll yield may times

    def many_yields
      yield(:peanut)
      yield(:butter)
      yield(:and)
      yield(:jelly)
    end

    def test_methods_can_call_yield_many_times
      result = []
      many_yields { |item| result << item }
      assert_equal [:peanut,:butter,:and,:jelly], result
    end

## blocks can be assigned to variables and called explicitly

    def test_blocks_can_be_assigned_to_variables_and_called_explicitly
      add_one = lambda { |n| n + 1 }
      assert_equal 11, add_one.call(10)

      # Alternative calling syntax
      assert_equal 11, add_one[10]
    end

## stand alone blocks can be passed to methods expecting blocks

    def test_stand_alone_blocks_can_be_passed_to_methods_expecting_blocks
      make_upper = lambda { |n| n.upcase }
      result = method_with_block_arguments(&make_upper)
      assert_equal "JIM", result
    end
    def method_with_block_arguments
      yield("Jim")
    end

## methods can take an explicit block argument

    def method_with_explicit_block(&block)
      block.call(10)
    end

    def test_methods_can_take_an_explicit_block_argument
      assert_equal 20, method_with_explicit_block { |n| n * 2 }

      add_one = lambda { |n| n + 1 }
      assert_equal 11, method_with_explicit_block(&add_one)
    end


# about class method

## three ways to write class methods

    class Dog

      def Dog.a_class_method
        :dogs_class_method
      end
    
      def self.class_method2
        :another_way_to_write_class_methods
      end
    
      class << self
        def another_class_method
          :still_another_way
        end
      end
    
    end

## class << self vs self.method

  *from [stackoverflow](http://stackoverflow.com/questions/10964081/class-self-vs-self-method-with-ruby-whats-better)*

  > class << self is good at keeping all of your class methods in the same block. If methods are being added in def self.method form then there's no guarantee (other than convention and wishful thinking) that there won't be an extra class method tucked away later in the file.

  > def self.method is good at explicitly stating that a method is a class method, whereas with class << self you have to go and find the container yourself.

  > Which of these is more important to you is a subjective decision, and also depends on things like how many other people are working on the code and what their preferences are.



# about methods

## public methods

    def my_method_in_the_same_class(a, b)
      a * b
    end

    def test_calling_methods_in_same_class
      assert_equal 12, my_method_in_the_same_class(3,4)
    end

    def test_calling_methods_in_same_class_with_explicit_receiver
      assert_equal 12, self.my_method_in_the_same_class(3,4)
    end

## private methods

    def my_private_method
      "a secret"
    end
    private :my_private_method

    def test_calling_private_methods_without_receiver
      assert_equal "a secret", my_private_method
    end

    def test_calling_private_methods_with_an_explicit_receiver
      exception = assert_raise(NoMethodError) do
        self.my_private_method
      end
      assert_match /my_private_method/, exception.message
    end

## understanding private method in Ruby

  *form [stackoverflow](http://stackoverflow.com/questions/4293215/understanding-private-methods-in-ruby)*

  > What private means in Ruby is a method cannot be called with an explicit receivers, e.g. some_instance.private_method(value). So even though the implicit receiver is self, in your example you explicitly use self so the private methods are not accessible.

  > Think of it this way, would you expect to be able to call a private method using a variable that you have assigned to an instance of a class? No. Self is a variable so it has to follow the same rules. However when you just call the method inside the instance then it works as expected because you aren't explicitly declaring the receiver.

