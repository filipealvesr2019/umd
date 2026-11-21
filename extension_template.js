const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function activate(context) {
    context.subscriptions.push(
        vscode.window.registerCustomEditorProvider(
            'umd.editor',
            new UmdEditorProvider(context),
            {
                webviewOptions: { retainContextWhenHidden: true },
                supportsMultipleEditorsPerDocument: false
            }
        )
    );
}

class UmdEditorProvider {
    constructor(context) {
        this.context = context;
    }

    async resolveCustomTextEditor(document, webviewPanel, token) {
        webviewPanel.webview.options = {
            enableScripts: true,
        };

        const htmlPath = path.join(__dirname, 'editor.html');
        const getHtml = () => {
            const template = fs.readFileSync(htmlPath, 'utf8');
            const initialContent = Buffer.from(document.getText(), 'utf8').toString('base64');
            return template.replace('__INITIAL_CONTENT_BASE64__', initialContent);
        };

        webviewPanel.webview.html = getHtml();

        let isInternalEdit = false;
        let lastAppliedText = document.getText();

        function updateWebview() {
            const currentText = document.getText();
            if (currentText === lastAppliedText) {
                return;
            }
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

        webviewPanel.webview.onDidReceiveMessage(e => {
            switch (e.type) {
                case 'ready':
                    updateWebview();
                    return;
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
