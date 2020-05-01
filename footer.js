'use strict';

const f_e = React.createElement;

class Footer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    return f_e("footer", {
      className: "footer"
    }, f_e("div", {
      className: 'container'
    }, f_e("p", {
      className: "text-muted"
    }, "Last Updated May 1, 2020")));
  }
}

const footerContainer = document.querySelector('#footer_container');
ReactDOM.render(e(Footer), footerContainer);
