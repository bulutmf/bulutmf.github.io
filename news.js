'use strict';

const n_e = React.createElement;

class News extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return n_e("div", {
        style: { 
          backgroundColor: "#f9f9f9", 
          padding: "15px", 
          borderRadius: "8px",
          borderLeft: "4px solid #337ab7"
        }
      },
      n_e("h3", {
        style: { marginTop: "0", marginBottom: "15px", color: "#333" }
      }, "📰 News"),
      n_e("ul", {
        style: { paddingLeft: "18px", marginBottom: "0", fontSize: "14px" }
      },
        n_e("li", {
          style: { marginBottom: "10px", lineHeight: "1.4" }
        },
          n_e("strong", null, "Dec 2025: "),
          "Presented our work on ",
          n_e("a", {
            href: "https://docs.google.com/presentation/d/1a6eVw_8GHwsz1ic2fbQLYsZBnt9m3NEf/edit?usp=sharing&ouid=114034349652044161485&rtpof=true&sd=true",
            target: "_blank"
          }, "autonomous detection engineering at ACSAC (Annual Computer Security Applications Conference)"),
          "—covering AI-driven detection authoring, reducing duplication, and lessons from building agentic security systems."
        ),
        n_e("li", {
          style: { marginBottom: "10px", lineHeight: "1.4" }
        },
          n_e("strong", null, "Nov 2025: "),
          "Interviewed on ",
          n_e("a", {
            href: "https://www.youtube.com/watch?v=DYzHYmtfiBY",
            target: "_blank"
          }, "Kesisen Yollar"),
          ", a YouTube channel featuring Turkish-born tech professionals in the US. ",
          n_e("em", null, "(In Turkish)")
        ),
        n_e("li", {
          style: { marginBottom: "10px", lineHeight: "1.4" }
        },
          n_e("strong", null, "Oct 2025: "),
          "Gave an invited talk on AI and Cybersecurity—what works and what doesn't—at the ",
          n_e("a", {
            href: "https://youtu.be/PiJpDvAMCg4?t=23457",
            target: "_blank"
          }, "Turkish Artificial Intelligence Summit 2025"),
          ". ",
          n_e("em", null, "(In Turkish)")
        ),
        n_e("li", {
          style: { marginBottom: "10px", lineHeight: "1.4" }
        },
          n_e("strong", null, "Sep 2025: "),
          "Gave an invited talk on ",
          n_e("a", {
            href: "https://docs.google.com/presentation/d/1PpmjJIvAo1sYSUoU1CGGCDVEfgFn2Us5/edit?rtpof=true&sd=true",
            target: "_blank"
          }, "\"Chasing Threat Actors with AI\""),
          " at the Artificial Unintelligence Conference."
        ),
        n_e("li", {
          style: { marginBottom: "10px", lineHeight: "1.4" }
        },
          n_e("strong", null, "Aug 2025: "),
          "Had a great conversation with Harness and Dewan about ",
          n_e("a", {
            href: "https://www.youtube.com/watch?v=UgMyFzQoq2M",
            target: "_blank"
          }, "AI and Security intersections"),
          ", covering detection engineering, AI hardening, and future possibilities."
        ),
        n_e("li", {
          style: { marginBottom: "0", lineHeight: "1.4" }
        },
          n_e("strong", null, "Feb 2025: "),
          "Spoke at the ",
          n_e("a", {
            href: "https://www.linkedin.com/posts/globalturksai_harvard-forum1-forum2-activity-7295446673139392513-RWlu?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAJ3_7sB_PtTXE-kDajKjaSm_3mZiJSWdto",
            target: "_blank"
          }, "Harvard AI Forum"),
          " on \"AI Research, Innovation, and Opportunities\" in collaboration with Harvard Business School."
        )
      )
    );
  }
}

const newsContainer = document.querySelector('#news_container');
ReactDOM.render(n_e(News), newsContainer);