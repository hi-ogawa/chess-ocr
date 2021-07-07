import * as React from "react";
import * as ReactDOM from "react-dom";
import App from "./app";

function main() {
  ReactDOM.render(React.createElement(App), document.querySelector("#root"));
}

main();
