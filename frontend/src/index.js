import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";

// Check if we are running inside the sidebar
const isSidebar = window.location.pathname.includes("sidebar");

const rootElement = document.getElementById("faultmaven-root") || document.getElementById("root");

// Mount the app
ReactDOM.render(
    <React.StrictMode>
        <App isSidebar={isSidebar} />
    </React.StrictMode>,
    rootElement
);
