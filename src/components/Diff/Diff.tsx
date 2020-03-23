import * as React from "react";
import { createRef, useEffect, useState } from "react";
import { DiffRow } from "./DiffRow";
// import { ipcRenderer } from "electron";

type DiffProps = {};
export const Diff = (props: DiffProps) => {
	const [file1, setFile1] = useState("");
	const [file2, setFile2] = useState("");

	const fileInput1 = createRef<HTMLInputElement>();
	const fileInput2 = createRef<HTMLInputElement>();

	const [output, setOutput] = useState<string[]>([]);
	const [errMsg, setErrMsg] = useState("");
	const [loading, setLoading] = useState(false);

	const diff = () => {
		if (file1 !== "" && file2 !== "") {
			(window as any).ipcRenderer.send("do-diff", [file1, file2]);
			setLoading(true);
		}
	};

	useEffect(() => {
		diff();
		// eslint-disable-next-line
	}, [file1, file2]);

	useEffect(() => {
		(window as any).ipcRenderer.on("diff-out", (event: any, args: { valid: boolean, data: string }) => {
			if (args.valid) {
				setErrMsg("");
				setOutput(args.data.split("\n"));
			} else {
				setErrMsg(args.data);
			}
			setLoading(false);
		});
		// eslint-disable-next-line
	}, []);
	return (
		<div>
			<div className="file-field input-field">
				<div className="btn">
					<span>File 1</span>
					<input ref={fileInput1} onChange={() => {
						const file = fileInput1.current!.files![0];
						if (file) {
							setFile1(file.path);
						} else {
							setFile1("");
						}
					}}
					       type="file"/>
				</div>
				<div className="file-path-wrapper">
					<input className="file-path" type="text"/>
				</div>
			</div>
			<div className="file-field input-field">
				<div className="btn">
					<span>File 2</span>
					<input ref={fileInput2} onChange={() => {
						const file = fileInput2.current!.files![0];
						if (file) {
							setFile2(file.path);
						} else {
							setFile2("");
						}
					}}
					       type="file"/>
				</div>
				<div className="file-path-wrapper">
					<input className="file-path" type="text"/>
				</div>
			</div>
			<div className="input-field">
				<a className="waves-effect green lighten-1 btn" onClick={() => diff()}>refresh</a>&nbsp;
			</div>
			<div>
				<div id="output">
					{loading ? <div className="progress">
						<div className="indeterminate"/>
					</div> : <div className="progress"><br/></div>}
					{errMsg === "" ?
						<table className="responsive-table">
							<thead>
							<tr>
								<th>Sheet</th>
								<th>Col</th>
								<th>Row</th>
								<th>Prev</th>
								<th>Curr</th>
							</tr>
							</thead>
							<tbody>
							{output.filter(item => item !== "").map(item => <DiffRow row={item}/>)}
							</tbody>
						</table> : <div>
							<pre className="white-text">{errMsg}</pre>
						</div>}
				</div>
			</div>
		</div>
	);
};
