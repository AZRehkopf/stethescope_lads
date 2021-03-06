const electron = require('electron');
const url = require('url');
const path = require('path');
const exec = require('child_process').execFile;
const {ipcMain, app, BrowserWindow, Menu} = electron;

//process.env.NODE_ENV = 'production'

let mainWindow;

app.on('ready', function() {
    // Generate first widnow
    mainWindow = new BrowserWindow({
        icon: path.join(__dirname, path.join('resources','favicon.ico')),
        resizable: false,
        height: 620,
        width: 800,
        webPreferences: {
            nodeIntegration: true
        }
    });
    // Load html file into the window 
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, path.join('resources', 'menu.html')),
        protocol: "file:",
        slashes: true
    }));
    // Remove menu bar
    // mainWindow.webContents.openDevTools()
    // Menu.setApplicationMenu(null);
});

app.on('window-all-closed', () => {
    app.quit();
});