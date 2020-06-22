import { app, BrowserWindow, ipcMain, protocol, shell } from "electron";
import { basename, dirname, extname, normalize, join } from "path";
import { exec } from "child_process";
import * as url from "url";

let mainWindow: BrowserWindow | null = null;

async function main() {
	mainWindow = new BrowserWindow({
		height: 768,
		width: 1333,
		title: "ExcelDiff",
		center: true,
		resizable: true,
		autoHideMenuBar: true,
		webPreferences: {nodeIntegration: true, preload: __dirname + "/preload.js"},
	});
	if (process.env.NODE_ENV === "development") {
		await mainWindow.loadURL("http://127.0.0.1:3000/");
	} else {
		await mainWindow.loadURL(url.format({
			pathname: "index.html",
			protocol: "file",
			slashes: true,
		}));
	}
	mainWindow.on("ready-to-show", mainWindow.show);
}

ipcMain.on("do-diff", (event, args) => {
	let cmd;
	if (process.env.NODE_ENV === "development") {
		console.log(args);
		cmd = `python ${process.cwd()}/exceldiff/exceldiff.py -t text "${args[0]}" "${args[1]}"`;
	} else {
		if (process.platform === "win32") {
			cmd = `${process.cwd()}/bin/exceldiff.exe -t text "${args[0]}" "${args[1]}"`;
		} else {
			cmd = `${process.cwd()}/bin/exceldiff -t text "${args[0]}" "${args[1]}"`;
		}
	}
	exec(cmd, (err, stdout, stderr) => {
		if (err) {
			mainWindow?.webContents.send("diff-out", {
				valid: false,
				data: stderr,
			});
			return;
		}

		if (stderr) {
			mainWindow?.webContents.send("diff-out", {
				valid: false,
				data: stderr,
			});
		} else {
			mainWindow?.webContents.send("diff-out", {
				valid: true,
				data: stdout,
			});
		}

	});
});

const getFileVersion = (filename: string): string => {
	const match = filename.match(/.*-([v.\d\w]+)\.xlsx/);
	return match ? match[1] : "";
};

const getOutFileName = (filename0: string, filename1: string): string => {
	const ver0 = getFileVersion(filename0);
	const ver1 = getFileVersion(filename1);
	return basename(filename0).replace(extname(filename0), "").replace(ver0, "") + `${ver0}-${ver1}-diff.xlsx`;
};


ipcMain.on("do-diff-file-open", (event, args) => {
	const filePath = dirname(args[0]);
	const fileName = getOutFileName(args[0], args[1]);
	console.log(join(filePath,fileName));
	shell.openItem(join(filePath,fileName));
});

ipcMain.on("do-diff-file", (event, args) => {
	let cmd;
	const filePath = dirname(args[0]);
	const fileName = getOutFileName(args[0], args[1]);

	if (process.env.NODE_ENV === "development") {
		console.log(args);
		cmd = `python ${process.cwd()}/exceldiff/exceldiff.py -t x "${args[0]}" "${args[1]}" -o ${filePath}/${fileName}`;
	} else {
		if (process.platform === "win32") {
			cmd = `${process.cwd()}/bin/exceldiff.exe -t x "${args[0]}" "${args[1]}" -o ${filePath}/${fileName}`;
		} else {
			cmd = `${process.cwd()}/bin/exceldiff -t x "${args[0]}" "${args[1]}" -o ${filePath}/${fileName}`;
		}
	}

	exec(cmd, (err, stdout, stderr) => {
		if (err) {
			mainWindow?.webContents.send("diff-out", {
				valid: false,
				data: stderr,
			});
			return;
		}

		if (stderr) {
			mainWindow?.webContents.send("diff-out", {
				valid: false,
				data: stderr,
			});
		} else {
			mainWindow?.webContents.send("diff-out", {
				valid: true,
				data: stdout,
			});
		}

	});
});

ipcMain.on("app-quit", () => process.exit(0));
app.on("ready", () => {
	if (process.env.NODE_ENV !== "development") {
		protocol.interceptFileProtocol("file", (request, callback) => {
			callback(normalize(`${__dirname}/${request.url.substr(7)}`));
		}, (err) => {
			if (err) console.error("Failed to register protocol");
		});
	}
	main();
});


