import { app, BrowserWindow, ipcMain } from "electron";
import { join } from "path";
import { exec } from "child_process";

let mainWindow: BrowserWindow | null = null;

async function main() {
	mainWindow = new BrowserWindow({
		height: 768,
		width: 1024,
		title: "ExcelDiff",
		center: true,
		resizable: true,
		autoHideMenuBar: true,
		webPreferences: {nodeIntegration: true, preload: __dirname + "/preload.js"},
	});
	if (process.env.NODE_ENV === "development") {
		await mainWindow.loadURL("http://127.0.0.1:3000/");
	} else {
		mainWindow.setMenu(null);
		await mainWindow.loadFile(join(__dirname, "resources/app", "index.html"));
	}
	mainWindow.on("ready-to-show", mainWindow.show);

}

ipcMain.on("do-diff", (event, args) => {
	let cmd;
	if (process.env.NODE_ENV === "development") {
		console.log(args);
		cmd = `${__dirname}/exceldiff -t text ${args[0]} ${args[1]}`;
	} else {
		cmd = `${process.cwd()}/exceldiff/exceldiff.exe -t text ${args[0]} ${args[1]}`;
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
	console.log(cmd);
});

ipcMain.on("app-quit", () => process.exit(0));
app.on("ready", main);



