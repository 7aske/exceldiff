import * as React from "react";
import { useEffect } from "react";

type DiffRowProps = {
	row: string
};
export const DiffRow = ({row}: DiffRowProps) => {
	useEffect(() => {
		console.log(row);
	}, [row]);
	return (
		<tr>
			{row.split("' '").map((str, i) => {
				if (str.startsWith("Unnamed: ")) {
					str = str.replace("Unnamed: ", "");
					let curr = parseInt(str);
					let out = curr > 26 ? String.fromCharCode((Math.floor(curr / 26)) + 64) : String.fromCharCode((curr + 65));
					while (curr > 26) {
						out += String.fromCharCode((Math.floor(curr / 26) + 65));
						curr -= 26;
					}
					str = out;
				} else if (i === 0) {
					str = str.substring(1);
				} else if (i === 1) {
					let curr = parseInt(str);
					let out = curr > 26 ? String.fromCharCode((Math.floor(curr / 26)) + 64) : String.fromCharCode((curr + 65));
					while (curr > 26) {
						out += String.fromCharCode((Math.floor(curr / 26) + 65));
						curr -= 26;
					}
					str = out;
				} else if (i === 2) {
					str = parseInt(str) + 2 + "";
				} else if (i === 4) {
					str = str.substring(0, str.length - 1);
				}
				return <td>{str}</td>;
			})}
		</tr>
	);
};
