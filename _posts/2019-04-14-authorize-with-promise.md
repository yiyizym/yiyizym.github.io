---
layout: post
title: 权限组件的 React 实现
date: 2019-04-13 17:20:28
excerpt: 实现思路和框架
categories: 
- tech
- frontend
---

**背景**

前段时间接了个任务，实现前端的权限管理功能。

权限本身简单来说要涉及如下功能：

- 如果登录用户没有相应的页面查看权限，当他进入相应页面时，只能看到一个简单的没有权限的文字提示

- 如果登录用户没有相应按钮的点击权限，当他点击相应按钮时，只能看到一个提示没有权限的弹窗

因为要调用接口获取用户的权限列表，所以得支持用异步判断用户有没有权限。

因为不同页面有不同的权限，在判断权限时还得获取当前页面的路由信息。

前端页面用 `Ant Design` 框架搭建，在 `Ant Design Pro` 这个框架有权限组件 [Authorized](https://pro.ant.design/components/Authorized-cn/) 。

当时（ 2019 年 3 月初）没有多想直接拿来用，后来发现这个组件里面有一大半的代码都没有被用到，更大的问题是坑挺多，比如这个[Authorized组件传入Promise页面会卡死](https://github.com/ant-design/ant-design-pro/issues/3558)，简直就是致命伤。

于是参考上面这个组件的思路，自己动手写了一个。下面大致写写思路，源码在[这里](https://github.com/yiyizym/authorize)。

**正文**

做产品的第一步，是写用户文档，写组件也是如此。

文档能告诉用户它有什么功能，该怎么用。写文档就是强逼你在写代码前思考怎样实现功能和让组件容易使用。

上面说到要实现两个权限功能：一个验证页面权限，另一个验证按钮权限。因此要向用户提供两个组件：`AuthorizedPage` 和 `AuthorizedBtn` 。下面是完整的文档：

```
##AuthorizedPage

实现用户有权限时可以查看页面，没有权限时只能看到 you dont have permissions 。

**用法示例**

假设用户需要拥有 page_a_read 权限才能查看 PageA 页面。只需要：

1 引入 AuthorizePage 组件 
2 照常编写页面组件 
3 在 export 前，调用 AuthorizePage('page_a_read')(PageA)

import AuthorizePage from 'path/to/AuthorizedPage';

class PageA extends Component {
  public render(): React.ReactNode {
    return (
      <div>page a</div>
    );
  }
}

export default AuthorizePage('page_a_read')(PageA);

**补充说明**

因为权限组件需要用到当前路由的信息，已经在内部引入了 react-router-dom 的 withRouter。所以可以直接在组件的 props 中访问相关路由属性。

##AuthorizedBtn

实现用户点击按钮，有权限时可以调用正常的 onClick 回调，没有权限时只触发提示： please apply for permission 。

**用法示例**

假设用户需要拥有 page_a_write 权限才能点击按钮say hello。只需要：

1 引入 AuthorizedBtn 组件 
2 在使用 AuthorizedBtn 时传入 currentAuthority 属性，其值为 page_a_write 。

import AuthorizedBtn from 'path/to/AuthorizedBtn';

class PageA extends Component {
  private sayHello(): void {

  }
  public render(): React.ReactNode {
    return (
      <AuthorizedBtn currentAuthority='page_a_write' onClick={() => this.sayHello()} type="primary">click to say hello</AuthorizedBtn>
    );
  }
}

export default PageA;

**补充说明**

因为权限组件需要用到当前路由的信息，已经在内部引入了 react-router-dom 的 withRouter。所以可以直接在组件的 props 中访问相关路由属性。
```

实现以上两个组件的核心思路就是：根据权限的有无，渲染不同的组件。因为需要异步判断权限，所以要异步渲染组件。

异步渲染组件就是先渲染一个占位用的组件（或 `null`），发送请求，然后根据返回结果把 React state 更新为`有权限组件`或`无权限组件`，触发重新渲染。

把实现这个核心思路的组件命名为 `BaseAuthorize` 。代码框架如下：

```JSX
class BaseAuthorize extends React.Component {

  public state = {
    component: null,
  };

  public componentDidMount(): void {
    this.setRenderComponent();
  }

  private setRenderComponent(): void {
    const { author } = this.props; // author 为实现异步判断权限的 Promise 实例
    author
      .then(() => {
        this.setState({
          component: okComponent, // 有权限时用 okComponent 更新 state
        });
      })
      .catch(() => {
        this.setState({
          component: errorComponent, // 无权限时用 errorComponent 更新 state
        });
      });
  }

  public render(): JSX.Element {
    const { component: Component } = this.state;
    if (Component === null) {
      return <div>loading...</div>;
    } else {
      return  <Component />
    }
  }
}
```

从上面的代码看出，`BaseAuthorize` 至少需要接收三个信息，一个是用于异步判断权限的 Promise 实例：`author` ，另外两个用来生成用于更新 state 的组件：okComponent 和 errorComponent。

实际的代码因为要处理很多问题，会复杂一点。

比如要异步设置 state ，当 Promise 状态变为 fullfilled 之前，组件因为各种原因被移除出 DOM ，此后调用 `setState` 方法会报 `warning` 。

如何根据传入的信息生成 okComponent 和 errorComponent 也是个问题，因为我们要应对这样一种情况：`okComponent` 的属性有可能会更新，比如按钮的状态由 disable 变为 enable，此时需要渲染带上新状态的 `okComponent` ，上面的代码显然没有办法做到，它连 `okComponent` 的属性有所更新都不知道。

在 `BaseAuthorize` 的基础上，再实现 `AuthorizePage` 和 `AuthorizedBtn` 。它们要向 `BaseAuthorize` 提供上面提到的三个信息，此外还要提供路由信息，以 `AuthorizePage` 为例，代码框架如下：

```JSX
class AuthorizePageInner extends React.Component {
  public render(): JSX.Element {
    // noMatch 是无权限时渲染的组件
    const noMatch = <div>  you don&apos;t have permissions  </div>;
    // page 是有权限时渲染的组件
    // currentAuthority 是 page 组件的固有权限
    // rest 作为 page 的属性传到  BaseAuthorize 里
    // staticContext 只是为了解决 warning 而从 rest 中提出来
    const { staticContext: any, page: Page, currentAuthority,  ...rest } = this.props;
    const { author } = this.state;
    return (<BaseAuthorize
      author={authorize(currentAuthority, match)}
      noMatch={noMatch}
      childrenProps={rest}
    >
      <Page />
    </BaseAuthorize>);
  }
}

// 这里要引用 react-router 的 withRouter 方法，注入路由信息
const AuthorizePage = (currentAuthority): Function => (page) => {
  return withRouter(props => <AuthorizePageInner key={props.match.url} currentAuthority={currentAuthority} page={page} {...props}/>);
};
```

上面代码中的 `authorize` 是一个实现异步获取、验证权限的 Promise 实例，它的代码框架如下：

```JSX
const getLoginUserInfo = async () => {

  // 如果已经从后台获取过登录用户的权限，可以保存下来，后续直接用
  // 如果没有从后台拿过，就发请求拿

};

const isHasPermission = (
  loginUserPermission, 
  currentAuthority, 
  match) => {
    // 根据当前登录用户拥有的权限/当前组件所需要的权限/以及当前页面的路由信息
    // 判断当前登录用户有没有访问的权限
}

const authorize = (currentAuthority, match) => {
  return new Promise((resolve, reject) => {
    return getLoginUserInfo().then(permission => {
      if (isHasPermission(permission, currentAuthority, match)) {
        resolve(true);
      } else {
        reject(false);
      }
    });
  });
};
```

以上就是大致的权限组件的实现，最终的实现和 demo 见[这里](https://github.com/yiyizym/authorize)。