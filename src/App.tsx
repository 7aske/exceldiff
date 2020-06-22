import React from "react";
import "./App.css";
import "materialize-css/dist/css/materialize.min.css";
import "./assets/css/materialize.css";
import "./assets/css/material-icons.css";
import "./assets/css/common.css";
import "materialize-css";
import { Diff } from "./components/Diff/Diff";

function App() {
	return (
		<div className="App">
			<Diff/>
		</div>
	);
}

export default App;
