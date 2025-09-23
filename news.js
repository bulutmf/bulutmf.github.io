'use strict';

const n_e = React.createElement;

class News extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return n_e("div", null,
      n_e("div", {
        className: "page-header"
      }, 
        n_e("h1", null, "News")
      ),
      n_e("div", {
        className: "lead"
      },
        n_e("ul", {
          style: { paddingLeft: "20px" }
        },
          n_e("li", {
            style: { marginBottom: "12px", lineHeight: "1.4" }
          },
            n_e("strong", {
              style: { color: "#555" }
            }, "September 2025: "),
            "Gave a talk on ",
            n_e("a", {
              href: "https://docs.google.com/presentation/d/1PpmjJIvAo1sYSUoU1CGGCDVEfgFn2Us5/edit?rtpof=true&sd=true",
              target: "_blank"
            }, "\"Chasing Threat Actors with AI\""),
            " at the Artificial Unintelligence Conference."
          ),
          n_e("li", {
            style: { marginBottom: "12px", lineHeight: "1.4" }
          },
            n_e("strong", {
              style: { color: "#555" }
            }, "August 2025: "),
            "Had a great conversation with Harness and Dewan about ",
            n_e("a", {
              href: "https://www.youtube.com/watch?v=UgMyFzQoq2M",
              target: "_blank"
            }, "AI and Security intersections"),
            ", covering detection engineering, AI hardening, and future possibilities."
          ),
          n_e("li", {
            style: { marginBottom: "12px", lineHeight: "1.4" }
          },
            n_e("strong", {
              style: { color: "#555" }
            }, "February 2025: "),
            "Spoke at the ",
            n_e("a", {
              href: "https://www.linkedin.com/posts/globalturksai_harvard-forum1-forum2-activity-7295446673139392513-RWlu?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAJ3_7sB_PtTXE-kDajKjaSm_3mZiJSWdto",
              target: "_blank"
            }, "Harvard AI Forum"),
            " on \"AI Research, Innovation, and Opportunities\" in collaboration with Harvard Business School."
          )
        )
      )
    );
  }
}

const newsContainer = document.querySelector('#news_container');
ReactDOM.render(n_e(News), newsContainer);