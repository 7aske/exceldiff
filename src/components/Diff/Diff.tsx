import * as React from "react";
import { createRef, useEffect, useRef, useState } from "react";
import { DiffRow } from "./DiffRow";
// import { ipcRenderer } from "electron";

type DiffProps = {};
export const Diff = (props: DiffProps) => {
	const [file1, setFile1] = useState("");
	const [file2, setFile2] = useState("");
	// const [disabled, setDisabled] = useState(true);

	const fileInput1 = createRef<HTMLInputElement>();
	const fileInput2 = createRef<HTMLInputElement>();

	const _floatingActionButtonRef = createRef<HTMLDivElement>();
	const floatingActionButtonRef = useRef<any>();
	const _openExternalRef = createRef<HTMLAnchorElement>();
	const openExternalRef = useRef<any>();
	const _generateDiffFileRef = createRef<HTMLAnchorElement>();
	const generateDiffFileRef = useRef<any>();


	const [output, setOutput] = useState<string[]>([]);
	const [errMsg, setErrMsg] = useState("");
	const [loading, setLoading] = useState(false);

	const diff = () => {
		if (file1 !== "" && file2 !== "") {
			(window as any).ipcRenderer.send("do-diff", [file1, file2]);
			setLoading(true);
		}
	};

	const diffFile = () => {
		if (file1 !== "" && file2 !== "") {
			(window as any).ipcRenderer.send("do-diff-file", [file1, file2]);
			setLoading(true);
		}
	};

	const openExternal = () => {
		if (file1 !== "" && file2 !== "") {
			(window as any).ipcRenderer.send("do-diff-file-open", [file1, file2]);
		}
	};

	const toggleDisabled = (args: any) => {
		if (generateDiffFileRef.current) {
			if (args.exists) {
				generateDiffFileRef.current.classList.remove("disabled");
			} else {
				generateDiffFileRef.current.classList.add("disabled");
			}
		}

	};

	const openExternalToggleDisabled = (args: any) => {

		if (openExternalRef.current) {
			if (args.exists) {
				openExternalRef.current.classList.remove("disabled");
			} else {
				openExternalRef.current.classList.add("disabled");
			}
		}
	};

	const reloadTooltips = () => {
		M.Tooltip.init(document.querySelectorAll(".tooltipped"), {});
	};

	useEffect(() => {
		diff();
		toggleDisabled({exists: file1 && file2});

		if (!file1 && !file2) {
			openExternalToggleDisabled({exists: false});
		}
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

		// hacky hacky code
		if (_openExternalRef.current) {
			openExternalRef.current = _openExternalRef.current;
		}

		if (_floatingActionButtonRef.current) {
			floatingActionButtonRef.current = _floatingActionButtonRef.current;
		}

		if (_generateDiffFileRef.current) {
			generateDiffFileRef.current = _generateDiffFileRef.current;
		}

		(window as any).ipcRenderer.on("diff-file-exists", (event: any, args: { exists: boolean }) => {
			openExternalToggleDisabled(args);
		});

		reloadTooltips();

		if (floatingActionButtonRef.current) {
			M.FloatingActionButton.init(floatingActionButtonRef.current, {
				hoverEnabled: true,
			});
		}

		// eslint-disable-next-line
	}, []);

	return (
		<div>
			<div className="file-field input-field">
				<div className="btn">
					<span>File 1</span>
					<input ref={fileInput1} onChange={() => {
						const file = fileInput1.current!.files![0];
						setFile1(file ? file.path : "");
					}} type="file"/>
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
						setFile2(file ? file.path : "");
					}} type="file"/>
				</div>
				<div className="file-path-wrapper">
					<input className="file-path" type="text"/>
				</div>
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

			<div className="fixed-action-btn" ref={_floatingActionButtonRef}>
				<a className="btn-floating btn-large cyan">
					<i className="large material-icons">expand_less</i>
				</a>
				<ul>
					<li><a className="btn-floating amber disabled tooltipped" ref={_openExternalRef}
					       onClick={() => openExternal()}
					       data-position="left" data-tooltip="Open diff file">
						<i className="material-icons">open_in_new</i></a></li>
					<li><a className="btn-floating red disabled tooltipped" ref={_generateDiffFileRef}
					       onClick={() => diffFile()}
					       data-position="left" data-tooltip="Generate diff .xlsx file">
						<i className="material-icons">insert_drive_file</i></a></li>
					<li><a className="btn-floating green tooltipped" onClick={() => diff()}
					       data-position="left" data-tooltip="Refresh">
						<i className="material-icons">refresh</i></a></li>
				</ul>
			</div>

		</div>
	);
};
