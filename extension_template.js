const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function activate(context) {
    const provider = new UmdEditorProvider(context);
    const opts = {
        webviewOptions: { retainContextWhenHidden: true },
        supportsMultipleEditorsPerDocument: false
    };
    context.subscriptions.push(
        vscode.window.registerCustomEditorProvider('umd.editor', provider, opts),
        vscode.window.registerCustomEditorProvider('umd.markdownEditor', provider, opts),
        vscode.commands.registerCommand('umd.openWithUmd', async (uri) => {
            const targetUri =
                uri ||
                (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.uri) ||
                (vscode.window.tabGroups &&
                    vscode.window.tabGroups.activeTabGroup &&
                    vscode.window.tabGroups.activeTabGroup.activeTab &&
                    vscode.window.tabGroups.activeTabGroup.activeTab.input &&
                    vscode.window.tabGroups.activeTabGroup.activeTab.input.uri);
            if (!targetUri) return;
            await vscode.commands.executeCommand('vscode.openWith', targetUri, 'umd.markdownEditor');
        })
    );
}

class UmdEditorProvider {
    constructor(context) {
        this.context = context;
    }

    async resolveCustomTextEditor(document, webviewPanel, token) {
        const docDir = path.dirname(document.uri.fsPath);
        const roots = [vscode.Uri.file(docDir)];
        if (vscode.workspace.workspaceFolders) {
            for (const folder of vscode.workspace.workspaceFolders) {
                roots.push(folder.uri);
            }
        }
        const ensureResourceRoot = (dirPath) => {
            const norm = path.resolve(dirPath).toLowerCase();
            if (!roots.some(r => path.resolve(r.fsPath).toLowerCase() === norm)) {
                roots.push(vscode.Uri.file(dirPath));
                webviewPanel.webview.options = {
                    enableScripts: true,
                    localResourceRoots: roots,
                };
            }
        };
        webviewPanel.webview.options = {
            enableScripts: true,
            localResourceRoots: roots,
        };

        const docBaseUri = webviewPanel.webview.asWebviewUri(vscode.Uri.file(docDir)).toString();
        const htmlPath = path.join(__dirname, 'editor.html');
        const getHtml = () => {
            const template = fs.readFileSync(htmlPath, 'utf8');
            const initialContent = Buffer.from(document.getText(), 'utf8').toString('base64');
            return template
                .replace('__INITIAL_CONTENT_BASE64__', initialContent)
                .replace('__DOC_BASE_URI__', docBaseUri);
        };

        webviewPanel.webview.html = getHtml();

        let isInternalEdit = false;
        let lastAppliedText = document.getText();

        function updateWebview() {
            const currentText = document.getText();
            if (currentText === lastAppliedText) {
                return;
            }
            lastAppliedText = currentText;
            webviewPanel.webview.postMessage({
                type: 'update',
                text: currentText,
                uri: document.uri.toString()
            });
        }

        const changeDocSubscription = vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document.uri.toString() === document.uri.toString()) {
                if (!isInternalEdit) {
                    updateWebview();
                }
            }
        });

        let watcher = null;
        try {
            watcher = fs.watch(htmlPath, () => {
                try {
                    webviewPanel.webview.html = getHtml();
                } catch (err) {}
            });
        } catch (err) {}

        webviewPanel.onDidDispose(() => {
            changeDocSubscription.dispose();
            if (watcher) watcher.close();
        });

        const MIME_BY_EXT = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.bmp': 'image/bmp',
            '.avif': 'image/avif',
        };
        const fileToDataUri = (absPath) => {
            const ext = path.extname(absPath).toLowerCase();
            const mime = MIME_BY_EXT[ext] || 'application/octet-stream';
            const b64 = fs.readFileSync(absPath).toString('base64');
            return `data:${mime};base64,${b64}`;
        };

        const fetchUrlBuffer = (urlStr, redirectsLeft = 5) => new Promise((resolve, reject) => {
            const httpMod = urlStr.startsWith('https:') ? require('https') : require('http');
            const req = httpMod.get(urlStr, {
                headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
            }, (res) => {
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirectsLeft > 0) {
                    const nextUrl = new URL(res.headers.location, urlStr).toString();
                    res.resume();
                    return fetchUrlBuffer(nextUrl, redirectsLeft - 1).then(resolve, reject);
                }
                if (res.statusCode < 200 || res.statusCode >= 300) {
                    res.resume();
                    return reject(new Error('HTTP ' + res.statusCode));
                }
                const chunks = [];
                res.on('data', c => chunks.push(c));
                res.on('end', () => resolve({
                    contentType: (res.headers['content-type'] || '').split(';')[0].trim().toLowerCase(),
                    buffer: Buffer.concat(chunks),
                    finalUrl: urlStr,
                }));
            });
            req.on('error', reject);
            req.setTimeout(10000, () => { req.destroy(new Error('timeout')); });
        });

        const resolveRemoteImage = async (rawUrl) => {
            const first = await fetchUrlBuffer(rawUrl);
            if (first.contentType.startsWith('image/')) {
                return `data:${first.contentType};base64,${first.buffer.toString('base64')}`;
            }
            if (first.contentType.includes('html')) {
                const html = first.buffer.toString('utf8');
                const ogMatch =
                    html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i) ||
                    html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i) ||
                    html.match(/<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']/i) ||
                    html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+name=["']twitter:image["']/i);
                if (ogMatch && ogMatch[1]) {
                    const imgUrl = new URL(ogMatch[1].replace(/&amp;/g, '&'), first.finalUrl).toString();
                    const imgRes = await fetchUrlBuffer(imgUrl);
                    if (imgRes.contentType.startsWith('image/')) {
                        return `data:${imgRes.contentType};base64,${imgRes.buffer.toString('base64')}`;
                    }
                    return imgUrl;
                }
            }
            return null;
        };

        webviewPanel.webview.onDidReceiveMessage(async e => {
            switch (e.type) {
                case 'ready':
                    updateWebview();
                    return;
                case 'pick-image': {
                    const selected = await vscode.window.showOpenDialog({
                        canSelectMany: false,
                        openLabel: 'Open Image',
                        defaultUri: vscode.Uri.file(docDir),
                        filters: {
                            Images: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'avif']
                        }
                    });
                    if (!selected || !selected.length) return;
                    const chosenUri = selected[0];
                    const chosenPath = chosenUri.fsPath;
                    let relPath = path.relative(docDir, chosenPath);
                    let storedSrc = chosenPath.replace(/\\/g, '/');
                    if (relPath && !path.isAbsolute(relPath) && !relPath.startsWith('..\\..\\..\\..')) {
                        storedSrc = relPath.replace(/\\/g, '/');
                        if (!storedSrc.startsWith('.')) {
                            storedSrc = './' + storedSrc;
                        }
                    }
                    let displaySrc = '';
                    try {
                        displaySrc = fileToDataUri(chosenPath);
                    } catch (err) {
                        ensureResourceRoot(path.dirname(chosenPath));
                        displaySrc = webviewPanel.webview.asWebviewUri(chosenUri).toString();
                    }
                    webviewPanel.webview.postMessage({
                        type: 'image-picked',
                        requestId: e.requestId,
                        src: storedSrc,
                        webviewSrc: displaySrc,
                        alt: path.parse(chosenPath).name,
                    });
                    return;
                }
                case 'resolve-image': {
                    const rawSrc = (e.src || '').trim();
                    if (!rawSrc) {
                        webviewPanel.webview.postMessage({ type: 'image-resolved', requestId: e.requestId, webviewSrc: null });
                        return;
                    }
                    if (/^https?:\/\//i.test(rawSrc)) {
                        let resolved = null;
                        try {
                            resolved = await resolveRemoteImage(rawSrc);
                        } catch (err) {}
                        webviewPanel.webview.postMessage({
                            type: 'image-resolved',
                            requestId: e.requestId,
                            webviewSrc: resolved,
                        });
                        return;
                    }
                    const absPath = path.isAbsolute(rawSrc) ? rawSrc : path.resolve(docDir, rawSrc);
                    let localResolved = null;
                    if (fs.existsSync(absPath)) {
                        try {
                            localResolved = fileToDataUri(absPath);
                        } catch (err) {}
                    }
                    webviewPanel.webview.postMessage({
                        type: 'image-resolved',
                        requestId: e.requestId,
                        webviewSrc: localResolved,
                    });
                    return;
                }
                case 'edit':
                    lastAppliedText = e.text;
                    isInternalEdit = true;
                    const edit = new vscode.WorkspaceEdit();
                    const fullRange = new vscode.Range(
                        document.positionAt(0),
                        document.positionAt(document.getText().length)
                    );
                    edit.replace(document.uri, fullRange, e.text);
                    vscode.workspace.applyEdit(edit).then(() => {
                        setTimeout(() => {
                            isInternalEdit = false;
                        }, 100);
                    });
                    return;
            }
        });
    }
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
