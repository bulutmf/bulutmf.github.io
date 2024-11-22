'use strict';

const e = React.createElement;

class Navigation extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {

    var goBack = "";
    if (window.location.href.includes("is690") || window.location.href.includes("CSCI")) {
      goBack = "../";
    }

    console.log(goBack);

    return e("nav", {
      className: "navbar navbar-default navbar-fixed-top"
    }, e("div", {
      className: "container"
    }, e("div", {
      className: "navbar-header"
    }, e("button", {
      type: "button",
      className: "navbar-toggle collapsed",
      "data-toggle": "collapse",
      "data-target": "#navbar",
      "aria-expanded": "false",
      "aria-controls": "navbar"
    }, e("span", {
      className: "sr-only"
    }, "Toggle navigation"), e("span", {
      className: "icon-bar"
    }), e("span", {
      className: "icon-bar"
    }), e("span", {
      className: "icon-bar"
    })), e("a", {
      className: "navbar-brand",
      href: goBack + "index.html"
    }, "Muhammed Fatih Bulut")), e("div", {
      id: "navbar",
      className: "collapse navbar-collapse"
    }, e("ul", {
      className: "nav navbar-nav"
    }, e("li", {
      className: "active"
    }, e("a", {
      href: goBack + "index.html"
    }, "About")),  
    e("li", null, e("a", {
      href: goBack + "projects.html"
    }, "Projects")),
    e("li", null, e("a", {
      target: "_blank",
      href: "https://medium.com/@dataturka"
    }, "Blog")), e("li", {
      className: "dropdown"
    }, e("a", {
      href: "#",
      className: "dropdown-toggle",
      "data-toggle": "dropdown",
      role: "button",
      "aria-haspopup": "true",
      "aria-expanded": "false"
    }, "Teaching ", e("span", {
      className: "caret"
    })), e("ul", {
      className: "dropdown-menu"
    }, 
    e("li", null, e("a", {
      href: goBack + "CSCI-GA.2262-%E2%80%8B001/2021_spring.html"
    }, e("Text", {
      style: {textDecorationLine: 'line-through', textDecorationStyle: 'solid'}
    }, "CSCI-GA.2262-001 Spring/21"))
    ), 
    e("li", null, e("a", {
      href: goBack + "CSCI-GA.2262-%E2%80%8B001/2020_spring.html"
    }, e("Text", {
      style: {textDecorationLine: 'line-through', textDecorationStyle: 'solid'}
    }, "CSCI-GA.2262-001 Spring/20"))
    ), 
    e("li", null, e("a", {
      href: goBack + "is690q/index.html"
    }, e("Text", {
      style: {textDecorationLine: 'line-through', textDecorationStyle: 'solid'}
    }, "IS690Q Spring/16"))
    ))
    )))));
  }
}

const domContainer = document.querySelector('#nav_container');
ReactDOM.render(e(Navigation), domContainer);
